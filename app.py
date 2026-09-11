
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import  CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta
import os
from dotenv import load_dotenv




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH, override=True)

from extensions import limiter
from expense import Expense
from repository import ExpenseRepository
from service import ExpenseService
from auth import auth, users_table




app = Flask(__name__)

limiter.init_app(app)

FRONTEND_URL = os.getenv("FRONTEND_URL")

if not FRONTEND_URL:
    raise RuntimeError("FRONTEND_URL is not configured")

CORS(
    app,
    resources={
        r"/*": {
            "origins": [FRONTEND_URL]
        }}
    )


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_ALGORITHM"] = "HS256"

jwt = JWTManager(app)



app.register_blueprint(auth, url_prefix="/auth")



repo    = ExpenseRepository()
service = ExpenseService(repo)


users_table()


@app.route("/")
def home_page():
    return send_from_directory(BASE_DIR, "login.html")

@app.route("/login.html")
def login_page():
    return send_from_directory(BASE_DIR, "login.html")

@app.route("/admin.html")
def admin_page():
    return send_from_directory(BASE_DIR, "admin.html")

@app.route("/register.html")
def register_page():
    return send_from_directory(BASE_DIR, "register.html")

@app.route("/verify.html")
def verify_page():
    return send_from_directory(BASE_DIR, "verify.html")

@app.route("/index.html")
def index_page():
    return send_from_directory(BASE_DIR, "index.html")



def role_required(required_role):
    claims = get_jwt()

    if claims.get("role") != required_role:
        return False

    return True


 #Admin only

@app.route("/admin", methods=["GET"])
@jwt_required()
def admin_dashboard():

    if not role_required("admin"):
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    return jsonify({
        "success": True,
        "message": "Welcome to the admin dashboard"
    }), 200

@app.route("/admin/users", methods=["GET"])
@jwt_required()
def admin_users():
    if not role_required("admin"):
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    result = service.get_all_users()
    return jsonify(result), 200

@app.route("/admin/users/count", methods=["GET"])
@jwt_required()
def admin_total_users():

    if not role_required("admin"):
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    result = service.get_total_users()

    return jsonify(result), 200


@app.route("/admin/summary", methods=["GET"])
@jwt_required()
def admin_summary():

    if not role_required("admin"):
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    result = service.admin_summary()

    return jsonify(result), 200



@app.route("/admin/users/<int:user_id>",methods = ["DELETE"])
@jwt_required()
def delete_user(user_id):

    if not role_required("admin"):
         return jsonify({
                    "success": False,
                    "message": "Admin access required"
                }), 403
    
    current_admin_id = get_jwt_identity()

    if str(user_id) == current_admin_id:
        return jsonify({
            "success": False,
            "message": "You cannot perform this action on your own account"
        }), 403
    
    result = service.delete_user(user_id)
    if result["success"]:
            return jsonify(result), 200
    
    return jsonify(result), 404


@app.route("/admin/users/<int:user_id>/deactivate",methods = ["PATCH"])
@jwt_required()
def deactivate_user(user_id):

    if not role_required("admin"):
         return jsonify({
                    "success": False,
                    "message": "Admin access required"
                }), 403
    current_admin_id = get_jwt_identity()
    
    if str(user_id) == current_admin_id:
        return jsonify({
            "success": False,
            "message": "You cannot perform this action on your own account"
        }), 403
    
    result = service.deactivate_user(user_id)
    if result["success"]:
            return jsonify(result), 200
    
    return jsonify(result), 404


@app.route("/admin/users/<int:user_id>/activate",methods = ["PATCH"])
@jwt_required()
def activate_user(user_id):

    if not role_required("admin"):
         return jsonify({
                    "success": False,
                    "message": "Admin access required"
                }), 403
    
    result = service.activate_user(user_id)
    if result["success"]:
            return jsonify(result), 200
    
    return jsonify(result), 404

    
    


# Users

@app.route("/expenses", methods=["POST"])
@jwt_required()

def add_expense():
    current_user_id = get_jwt_identity()

    if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Request must be JSON"
            }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON data"
        }), 400

    result = service.add_expense(
        data.get("name"),
        data.get("amount"),
        data.get("category"),
        current_user_id,
    )

    if result["success"]:
        return jsonify(result), 201  
    return jsonify(result), 400




@app.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():

    current_user_id = get_jwt_identity()
    result = service.get_expenses_by_user(current_user_id)

    rows = result["data"]

    return jsonify({
        "success": True,
        "data": [
            {
                "id": r[0],
                "name": r[1],
                "amount": r[2],
                "category": r[3],
                "date": r[4]
            }
            for r in rows
        ]
    }), 200



@app.route("/expenses/search", methods=["GET"])
@jwt_required()
def search_by_name():
    current_user_id = get_jwt_identity()
    name = request.args.get("name")
    result = service.search_by_name(name, current_user_id)

    if not result["success"]:
        return jsonify(result), 400

    rows = result["data"]

    return jsonify({
        "success": True,
        "data": [
            {
                "id": r[0],
                "name": r[1],
                "amount": r[2],
                "category": r[3],
                "date": r[4]
            }
            for r in rows
        ]
    }), 200



@app.route("/expenses/<expense_id>", methods=["PUT"])
@jwt_required()
def update(expense_id):
    current_user_id = get_jwt_identity()
    if not request.is_json:
                return jsonify({
                    "success": False,
                    "message": "Request must be JSON"
                }), 400
    
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "Invalid JSON data"
            }), 400

    result = service.update_expense(expense_id,
        data.get("name"),
        data.get("amount"),
        data.get("category"),
        current_user_id
    )
    
    
    if result["success"]:
        return jsonify(result), 200
    return jsonify(result), 400


@app.route("/expenses/<expense_id>", methods=["DELETE"])
@jwt_required()
def delete(expense_id):
    current_user_id = get_jwt_identity()
    result = service.delete_expense(expense_id, current_user_id)
    if result["success"]:
        return jsonify(result), 200
    return jsonify(result), 404


@app.route("/expenses/total", methods=["GET"])
@jwt_required()
def total():
    current_user_id = get_jwt_identity()
    result = service.get_total_expenses(current_user_id)
    return jsonify(result), 200


@app.route("/expenses/filter", methods=["GET"])
@jwt_required()
def filter_by_category():
    current_user_id = get_jwt_identity()
    category = request.args.get("category")
    result = service.filter_by_category(category, current_user_id)
    if not result["success"]:
        return jsonify(result), 400
    
    rows = result["data"]
    return jsonify({
        "success": True,
        "data":[

        {"id": r[0],
        "name": r[1],
        "amount": r[2],
        "category": r[3], 
        "date": r[4]
        }
         for r in rows
         ]
    }), 200




@app.route("/expenses/count", methods=["GET"])
@jwt_required()
def count():
    current_user_id = get_jwt_identity()
    result = service.get_expense_count(current_user_id)
    return jsonify(result), 200


@app.route("/expenses/average", methods=["GET"])
@jwt_required()
def average():
    current_user_id = get_jwt_identity()
    result = service.get_average_amount(current_user_id)
    return jsonify(result), 200


@app.route("/expenses/categories/summary", methods=["GET"])
@jwt_required()
def category_summary():
    current_user_id = get_jwt_identity()
    result = service.get_amount_by_category(current_user_id)
    return jsonify(result), 200

@app.route("/expenses/minmax", methods=["GET"])
@jwt_required()
def minmax():
    current_user_id = get_jwt_identity()
    result = service.get_min_max(current_user_id)
    return jsonify(result), 200



ALLOWED_FILES = {"login.html", "register.html", "verify.html", "index.html","admin.html",
                         "style.css","admin.css", "auth.js", "script.js", "verify.js", "admin.js"}

@app.route("/<path:filename>")
def static_files(filename):
    if filename not in ALLOWED_FILES:
        return jsonify({"success": False, "message": "Not found"}), 404
    return send_from_directory(BASE_DIR, filename)

    
# ----------- RUN APP --------------
if __name__ == "__main__":
    app.run(debug=True)