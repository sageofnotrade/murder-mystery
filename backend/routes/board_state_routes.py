"""
Flask routes for board state synchronization (BE-008).
Handles getting, updating, and synchronizing detective board state.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.agents.board_agent import BoardAgent, BoardState
import redis
import os
import json
import logging

# Redis setup (assumes REDIS_URL in env)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

board_state_bp = Blueprint("board_state", __name__, url_prefix="/api/board")

# Helper: Redis key for board state

def get_board_redis_key(mystery_id):
    return f"board_state:{mystery_id}"

logger = logging.getLogger(__name__)

# GET: Retrieve board state for a mystery
@board_state_bp.route("/<mystery_id>", methods=["GET"])
@jwt_required()
def get_board_state(mystery_id):
    key = get_board_redis_key(mystery_id)
    data = redis_client.get(key)
    if not data:
        logger.error(f'Board state not found for mystery_id: {mystery_id}')
        return jsonify({"data": None, "error": "Board state not found"}), 404
    try:
        board_state = json.loads(data)
        return jsonify({"data": board_state, "error": None})
    except Exception as e:
        logger.error(f'Corrupted board state for mystery_id: {mystery_id}, error: {e}')
        return jsonify({"data": None, "error": "Corrupted board state"}), 500

# POST: Synchronize/update board state
@board_state_bp.route("/<mystery_id>/sync", methods=["POST"])
@jwt_required()
def sync_board_state(mystery_id):
    user_id = get_jwt_identity()
    payload = request.get_json()
    if not payload or "board_state" not in payload:
        logger.error(f'Missing board_state in request for mystery_id: {mystery_id}')
        return jsonify({"data": None, "error": "Missing board_state in request"}), 400
    # Validate board_state structure strictly
    board_state_input = payload["board_state"]
    if not isinstance(board_state_input, dict):
        logger.error(f'board_state must be a dict for mystery_id: {mystery_id}')
        return jsonify({"data": None, "error": "board_state must be a dict"}), 400
    required_keys = {"elements", "connections", "notes", "layout"}
    if not required_keys.issubset(board_state_input.keys()):
        logger.error(f'board_state missing required keys: {required_keys - set(board_state_input.keys())} for mystery_id: {mystery_id}')
        return jsonify({"data": None, "error": f"board_state missing required keys: {required_keys - set(board_state_input.keys())}"}), 400
    try:
        board_state = BoardState(**board_state_input).model_dump()
    except Exception as e:
        logger.error(f'Invalid board_state for mystery_id: {mystery_id}, error: {e}')
        return jsonify({"data": None, "error": f"Invalid board_state: {str(e)}"}), 400
    key = get_board_redis_key(mystery_id)
    redis_client.set(key, json.dumps(board_state))
    return jsonify({"data": board_state, "error": None})

# (Optional) PUT: Replace board state
@board_state_bp.route("/<mystery_id>", methods=["PUT"])
@jwt_required()
def replace_board_state(mystery_id):
    user_id = get_jwt_identity()
    payload = request.get_json()
    if not payload or "board_state" not in payload:
        logger.error(f'Missing board_state in request for mystery_id: {mystery_id}')
        return jsonify({"data": None, "error": "Missing board_state in request"}), 400
    try:
        board_state = BoardState(**payload["board_state"]).model_dump()
    except Exception as e:
        logger.error(f'Invalid board_state for mystery_id: {mystery_id}, error: {e}')
        return jsonify({"data": None, "error": f"Invalid board_state: {str(e)}"}), 400
    key = get_board_redis_key(mystery_id)
    redis_client.set(key, json.dumps(board_state))
    return jsonify({"data": board_state, "error": None})
