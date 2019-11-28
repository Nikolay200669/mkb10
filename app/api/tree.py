from peewee import fn, JOIN
from flask import jsonify, request
from app.models import MKB10


def get_classes():
    qs = (MKB10
          .select(MKB10.id, MKB10.name)
          .where(MKB10.parent >> None)
          .where(MKB10.code >> None))
    return jsonify(tuple(qs.dicts()))


def get_blocks(cls):
    qs = (MKB10
          .select(MKB10.id, MKB10.name)
          .where(MKB10.code >> None)
          .where(MKB10.parent == cls))
    return jsonify(tuple(qs.dicts()))


def get_group(block):
    Child = MKB10.alias()
    qs = (MKB10
          .select(MKB10.id, MKB10.code, MKB10.name,
                  (fn.count(Child.id) > 0).alias('ct'))
          .join(Child, JOIN.LEFT_OUTER, on=(Child.parent == MKB10.id))
          .where(MKB10.parent == block)
          .group_by(MKB10.id)
          .order_by(MKB10.code))
    qs = actual_filter(qs)
    # A little magic: `update()` method of dict always returns `None`
    # It means we always get `None or x` and return an updated dict
    result = map(lambda x: x.update(has_subgroup=bool(x.pop('ct'))) or x,
                 qs.dicts())
    return jsonify(tuple(result))


def get_subgroup(group):
    qs = (MKB10
          .select(MKB10.id, MKB10.code, MKB10.name)
          .where(MKB10.code.startswith(group + '.')))
    qs = actual_filter(qs)
    return jsonify(tuple(qs.dicts()))


def actual_filter(qs):
    # If the keyword in the args we add an actual flag to result set
    if 'all' in request.args:
        return qs.select_extend(MKB10.actual)
    # Otherwise we filter the result by actual flag
    return qs.where(MKB10.actual == True)
