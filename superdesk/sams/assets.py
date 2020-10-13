# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013-2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""The Assets API to retrieve, create, update, delete the list of ``Assets``.


=====================   =================================================
**endpoint name**        'assets'
**resource title**       'Assets'
**resource url**         [GET] '/sams/assets'
**item url**             [GET] '/sams/assets/<:class:`str`>'
**schema**               :attr:`sams_client.schemas.ASSET_SCHEMA`
=====================   =================================================
"""

import ast
import logging
import superdesk
from flask import request
from superdesk.errors import SuperdeskApiError
from .utils import get_file_from_sams
from superdesk.storage.superdesk_file import generate_response_for_file

logger = logging.getLogger(__name__)
assets_bp = superdesk.Blueprint('sams_assets', __name__)


@assets_bp.route('/sams/assets', methods=['GET'])
def get():
    """
    Returns a list of all the registered assets
    """
    assets = assets_bp.kwargs['client'].assets.search(params=request.args.to_dict())
    return assets.json(), assets.status_code


@assets_bp.route('/sams/assets/<item_id>', methods=['GET'])
def find_one(item_id):
    """
    Uses item_id and returns the corresponding
    asset
    """
    item = assets_bp.kwargs['client'].assets.get_by_id(item_id=item_id)
    return item.json(), item.status_code


@assets_bp.route('/sams/assets/binary/<item_id>', methods=['GET'])
def get_binary(item_id):
    """
    Uses item_id and returns the corresponding
    asset binary
    """
    file = get_file_from_sams(assets_bp.kwargs['client'], item_id)
    return generate_response_for_file(file)


@assets_bp.route('/sams/assets', methods=['POST'])
def create():
    """
    Creates new Asset
    """
    files = {'binary': request.files['binary']}
    docs = request.form.to_dict()
    post_response = assets_bp.kwargs['client'].assets.create(docs=docs, files=files)
    return post_response.json(), post_response.status_code


@assets_bp.route('/sams/assets/<item_id>', methods=['DELETE'])
def delete(item_id):
    """
    Uses item_id and deletes the corresponding asset
    """
    try:
        etag = request.headers['If-Match']
    except KeyError:
        raise SuperdeskApiError.badRequestError(
            "If-Match field missing in header"
        )

    delete_response = assets_bp.kwargs['client'].assets.delete(
        item_id=item_id, headers={'If-Match': etag}
    )
    if delete_response.status_code != 204:
        return delete_response.json(), delete_response.status_code
    return '', delete_response.status_code


@assets_bp.route('/sams/assets/<item_id>', methods=['PATCH'])
def update(item_id):
    """
    Uses item_id and updates the corresponding asset
    """
    try:
        etag = request.headers['If-Match']
    except KeyError:
        raise SuperdeskApiError.badRequestError(
            "If-Match field missing in header"
        )

    if request.files.get('binary'):
        # The binary data was supplied so this must be a multipart request
        # Get the updates from the `request.form` attribute
        files = {'binary': request.files['binary']}
        updates = request.form.to_dict()
    else:
        # Only the metadata was supplied so this must be a standard JSON request
        # Get the updates from the `request.get_json` function
        files = {}
        updates = request.get_json()

    update_response = assets_bp.kwargs['client'].assets.update(
        item_id=item_id,
        updates=updates,
        headers={'If-Match': etag},
        files=files
    )
    return update_response.json(), update_response.status_code


@assets_bp.route('/sams/assets/counts', methods=['GET'], defaults={'set_ids': None})
@assets_bp.route('/sams/assets/counts/<set_ids>', methods=['GET'])
def get_assets_count(set_ids):
    set_ids = ast.literal_eval(set_ids) if set_ids else None
    counts = assets_bp.kwargs['client'].assets.get_assets_count(
        set_ids=set_ids
    )
    return counts


@assets_bp.route("/sams/assets/compressed_binary/<asset_ids>", methods=["GET"])
def get_assets_compressed_binary(asset_ids):
    asset_ids = ast.literal_eval(asset_ids) if asset_ids else None
    zip_binary = assets_bp.kwargs["client"].assets.get_binary_zip_by_id(
        item_ids=asset_ids
    )
    return zip_binary.content
