from flask import Blueprint, request, jsonify, session
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    session.clear() 
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    user = User.query.filter_by(email=email, is_active=True).first()
    if not user:
        return jsonify({"error": "Invalid email"}), 401

    # 🔑 THIS IS THE CRITICAL PART
    session["user_id"] = user.id
    session["role"] = user.role
    session["organization_id"] = user.organization_id

    return jsonify({
        "message": "Login successful",
        "role": user.role
    })

@auth_bp.route("/me", methods=["GET"])
def me():
    if "role" not in session:
        return jsonify({"error": "unauthenticated"}), 401

    return jsonify({
        "user_id": session["user_id"],
        "role": session["role"]
    })
