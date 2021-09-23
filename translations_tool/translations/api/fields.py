from rest_framework import serializers


class CommaSeparatedListField(serializers.CharField):
    def to_internal_value(self, data):
        return data.split(",")
