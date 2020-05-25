import datetime
import logging

from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView,\
    RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from jogs.managers.jog_manager import JogManager
from jogs.models import Jog, JogReport
from jogs.permissions import UserIsOwnerOrAdmin
from jogs.serializers.jog import JogSerializer
from jogs.serializers.jog_report import JogReportSerializer

from utils.filters.commons import FilterListMixin
from utils.filters.parser import ParsingException
from utils.permissions import is_admin


logger = logging.getLogger('jogtrack')
logger.setLevel(logging.DEBUG)


class JogListCreateView(ListCreateAPIView, FilterListMixin):
    """ View class to create and list a jog entries."""
    serializer_class = JogSerializer
    permission_classes = (IsAuthenticated,)
    filter_fields = {
        'id': int,
        'user__pk': int,
        'date': datetime.date,
        'distance': int,
        'time': int,
        'country': str,
        'city': str
    }

    def get_queryset(self):
        filters = self.get_search_filters()

        if is_admin(self.request.user):
            qs = Jog.objects.all()
            if filters:
                return qs.filter(filters)
            return qs
        else:
            qs = Jog.objects.filter(user=self.request.user)
            if filters:
                return qs.filter(filters)
            return qs

    def list(self, request, *args, **kwargs):
        """ This is called on GET requests."""
        try:
            response = super().list(request, *args, **kwargs)
        except ParsingException as err:
            return Response(
                str(err),
                status=status.HTTP_400_BAD_REQUEST
            )

        return response

    def post(self, request, *args, **kwargs):
        jog_serializer = JogSerializer(data=request.data,
                                       context={'request': request})
        if jog_serializer.is_valid():
            jog = JogManager.create_jog(jog_serializer, request.user)

            return Response(
                JogSerializer(jog).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            jog_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class JogRUDView(RetrieveUpdateDestroyAPIView):
    """ View class to retrieve, update and delete a jog entry."""
    serializer_class = JogSerializer
    queryset = Jog.objects.all()
    permission_classes = (IsAuthenticated, UserIsOwnerOrAdmin)

    def _update_jog(self, new_data, partial=False):
        """ Updates a jog."""
        old_jog = self.get_object()
        new_jog_s = JogSerializer(old_jog, data=new_data, partial=partial)
        if new_jog_s.is_valid():
            new_jog = JogManager(old_jog).update_jog(new_jog_s, partial)
            return JogSerializer(new_jog).data, None

        return None, new_jog_s.errors

    def update(self, request, *args, **kwargs):
        jog_data, errors = self._update_jog(request.data)
        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            data=jog_data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        jog_data, errors = self._update_jog(request.data, partial=True)
        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            data=jog_data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        jog = self.get_object()
        ret = super().delete(request, *args, **kwargs)
        JogManager(jog).on_jog_cud()
        return ret


class JogReportListView(ListAPIView, FilterListMixin):
    """ View class to create and list a jog entries."""
    serializer_class = JogReportSerializer
    permission_classes = (IsAuthenticated,)
    filter_fields = {
        'id': int,
        'user__pk': int,
        'start_date': datetime.date,
        'end_date': datetime.date,
    }

    def get_queryset(self):
        filters = self.get_search_filters()

        if is_admin(self.request.user):
            qs = JogReport.objects.all()
            if filters:
                return qs.filter(filters)
            return qs
        else:
            qs = JogReport.objects.filter(user=self.request.user)
            if filters:
                return qs.filter(filters)
            return qs
