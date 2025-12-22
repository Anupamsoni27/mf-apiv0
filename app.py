from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200"]}}, supports_credentials=True)

# --------------------------
# MONGO CONNECTION
# --------------------------

client = MongoClient("mongodb+srv://anupamsoni27:Mystuff8358%401@india-01.kwer3ek.mongodb.net/", tlsAllowInvalidCertificates=True)
db = client["mf_data"]

fund_holdings = db["fund_holdings_test"]
stocks = db["stocks"]
stock_timelines = db["stock_timelines"]
favorites = db["favorites"]
users = db["users"]

# Indexes for favorites
favorites.create_index([("userId", 1), ("itemType", 1)])
favorites.create_index([("userId", 1), ("itemId", 1), ("itemType", 1)], unique=True)


# --------------------------
# Helper Response Method
# --------------------------
def make_response(status="success", message="", records=None, count=None, data=None):
    response = {"status": status, "message": message}
    if records is not None:
        response["records"] = records
    if count is not None:
        response["count"] = count
    if data is not None:
        response["data"] = data
    return jsonify(response)


# ============================================================================
# USER ENDPOINTS (NO JWT)
# ============================================================================

@app.route("/api/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")

        if not name or not email:
            return make_response(status="error", message="name and email required"), 400

        existing = users.find_one({"email": email})
        if existing:
            existing["_id"] = str(existing["_id"])
            return make_response(status="success", message="User already exists", data=existing)

        new_user = {
            "name": name,
            "email": email,
            "picture": data.get("picture"),
            "phoneNumber": data.get("phoneNumber"),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        result = users.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)

        return make_response(status="success", message="User created", data=new_user), 201

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/users", methods=["GET"])
def get_user_by_email():
    try:
        email = request.args.get("email")
        if not email:
            return make_response(status="error", message="email required"), 400

        user = users.find_one({"email": email})
        if not user:
            return make_response(status="error", message="User not found"), 404

        user["_id"] = str(user["_id"])
        return make_response(status="success", message="User fetched", data=user)

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/users/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return make_response(status="error", message="User not found"), 404

        user["_id"] = str(user["_id"])
        return make_response(status="success", message="User fetched", records=user)

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json()
        data["updatedAt"] = datetime.utcnow()

        result = users.update_one({"_id": ObjectId(user_id)}, {"$set": data})

        if result.matched_count == 0:
            return make_response(status="error", message="User not found"), 404

        updated_user = users.find_one({"_id": ObjectId(user_id)})
        updated_user["_id"] = str(updated_user["_id"])

        return make_response(status="success", message="User updated", data=updated_user)

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        result = users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return make_response(status="error", message="User not found"), 404

        return make_response(status="success", message="User deleted")

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/users/all", methods=["GET"])
def list_all_users():
    try:
        user_list = []
        for u in users.find():
            u["_id"] = str(u["_id"])
            user_list.append(u)

        return make_response(status="success", message="Users fetched", count=len(user_list), records=user_list)

    except Exception as e:
        return make_response(status="error", message=str(e))


# ============================================================================
# FUNDS API
# ============================================================================

@app.route("/getAllFunds", methods=["GET"])
def get_all_funds():
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 50))

        sort_by = request.args.get("sort_by", "holding_count")
        order = request.args.get("order", "desc")
        sort_direction = -1 if order == "desc" else 1

        date_filter = request.args.get("date")
        if not date_filter:
            latest_doc = fund_holdings.find_one(sort=[("date", -1)])
            if not latest_doc:
                return make_response(status="error", message="No records found")
            date_filter = latest_doc["date"]

        total_count = fund_holdings.count_documents({"date": date_filter})

        pipeline = [
            {"$match": {"date": date_filter}},
            {"$group": {
                "_id": "$unique_id",
                "name": {"$first": "$name"},
                "holding_count": {"$max": "$holding_count"},
                "added_count": {"$max": "$added_count"},
                "removed_count": {"$max": "$removed_count"},
                "latest_date": {"$max": "$date"}
            }},
            {"$sort": {sort_by: sort_direction}},
            {"$skip": skip},
            {"$limit": limit}
        ]

        results = list(fund_holdings.aggregate(pipeline))

        return make_response(
            status="success",
            message="Funds fetched",
            records=results,
            count=total_count
        )

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/getFundInfo", methods=["GET"])
def get_fund_info():
    try:
        fund_id = request.args.get("fund_id")
        date = request.args.get("date")

        if not fund_id:
            return make_response(status="error", message="fund_id required"), 400

        query = {"unique_id": fund_id}
        if date:
            query["date"] = date

        fund_records = list(fund_holdings.find(query))

        date_counts = [{"date": f["date"], "holding_count": f["holding_count"]} for f in fund_records]

        latest = list(fund_holdings.find(query).sort("date", -1).limit(1))
        if not latest:
            return make_response(status="error", message="Fund not found")

        record = latest[0]
        record["_id"] = str(record["_id"])
        record["fund_count"] = date_counts

        return make_response(status="success", message="Fund info fetched", records=record)

    except Exception as e:
        return make_response(status="error", message=str(e))


# ============================================================================
# STOCKS API
# ============================================================================

@app.route("/getAllStocks", methods=["GET"])
def get_all_stocks():
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 50))

        sort_by = request.args.get("sort_by", "name")
        order = request.args.get("order", "asc")
        sort_direction = -1 if order == "desc" else 1

        search = request.args.get("search", "").strip()

        query = {}
        if search:
            query["name"] = {"$regex": search, "$options": "i"}

        total_count = stocks.count_documents(query)

        results = list(
            stocks.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit)
        )

        # Convert IDs
        for s in results:
            s["_id"] = str(s["_id"])

        return make_response(
            status="success",
            message="Stocks fetched",
            records=results,
            count=total_count
        )

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/getStockInfo", methods=["GET"])
def get_stock_info():
    try:
        stock_id = request.args.get("stock_id")
        if not stock_id:
            return make_response(status="error", message="stock_id required"), 400

        stock = stocks.find_one({"_id": ObjectId(stock_id)})
        if not stock:
            return make_response(status="error", message="Stock not found")

        stock["_id"] = str(stock["_id"])
        return make_response(status="success", message="Stock fetched", records=stock)

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/getStockTimeline", methods=["GET"])
def get_stock_timeline():
    try:
        stock_id = request.args.get("stock_id")
        if not stock_id:
            return make_response(status="error", message="stock_id required"), 400

        timeline = stock_timelines.find_one({"_id": stock_id})
        if not timeline:
            return make_response(status="error", message="Timeline not found")

        timeline["_id"] = str(timeline["_id"])
        return make_response(status="success", message="Timeline fetched", records=timeline)

    except Exception as e:
        return make_response(status="error", message=str(e))


# ============================================================================
# FAVORITES API (NO AUTH)
# ============================================================================

@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    try:
        user_id = request.args.get("userId")
        item_type = request.args.get("type")

        if not user_id:
            return make_response(status="error", message="userId required"), 400

        query = {"userId": user_id}
        if item_type:
            query["itemType"] = item_type

        favs = list(favorites.find(query))

        stocks_list = []
        funds_list = []

        for f in favs:
            if f["itemType"] == "stock":
                stocks_list.append({"id": f["itemId"], "name": f.get("itemName", "")})
            else:
                funds_list.append({"id": f["itemId"], "name": f.get("itemName", "")})

        return make_response(
            status="success",
            message="Favorites fetched",
            data={"stocks": stocks_list, "funds": funds_list},
            count=len(favs)
        )

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        item_id = data.get("itemId")
        item_type = data.get("itemType")
        item_name = data.get("itemName", "")

        if not user_id or not item_id or not item_type:
            return make_response(status="error", message="userId, itemId, itemType required"), 400

        existing = favorites.find_one({
            "userId": user_id,
            "itemId": item_id,
            "itemType": item_type
        })

        if existing:
            return make_response(status="success", message="Already in favorites")

        fav = {
            "userId": user_id,
            "itemId": item_id,
            "itemType": item_type,
            "itemName": item_name,
            "createdAt": datetime.utcnow()
        }

        favorites.insert_one(fav)
        fav["_id"] = str(fav["_id"])
        return make_response(status="success", message="Added", data=fav)

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/favorites/<item_id>", methods=["DELETE"])
def remove_favorite(item_id):
    try:
        user_id = request.args.get("userId")
        item_type = request.args.get("type")

        if not user_id or not item_type:
            return make_response(status="error", message="userId and type required"), 400

        result = favorites.delete_one({
            "userId": user_id,
            "itemId": item_id,
            "itemType": item_type
        })

        if result.deleted_count == 0:
            return make_response(status="error", message="Favorite not found"), 404

        return make_response(status="success", message="Removed")

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/favorites/rpc/add", methods=["POST"])
def add_favorite_rpc():
    return add_favorite()


@app.route("/api/favorites/rpc/remove", methods=["POST"])
def remove_favorite_rpc():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        item_id = data.get("itemId")
        item_type = data.get("itemType")

        if not user_id or not item_id or not item_type:
            return make_response(status="error", message="userId, itemId, itemType required"), 400

        result = favorites.delete_one({
            "userId": user_id,
            "itemId": item_id,
            "itemType": item_type
        })

        if result.deleted_count == 0:
            return make_response(status="error", message="Favorite not found"), 404

        return make_response(status="success", message="Removed")

    except Exception as e:
        return make_response(status="error", message=str(e))

@app.route("/api/favorites/stocks", methods=["GET"])
def get_favorite_stocks():
    try:
        user_id = request.args.get("userId")
        if not user_id:
            return make_response(status="error", message="userId required"), 400

        favs = list(favorites.find({"userId": user_id, "itemType": "stock"}))
        ids = [f["itemId"] for f in favs]

        if not ids:
            return make_response(status="success", message="No favorites", count=0, records=[])

        try:
            obj_ids = [ObjectId(i) for i in ids]
            results = list(stocks.find({"_id": {"$in": obj_ids}}))
        except:
            results = list(stocks.find({"_id": {"$in": ids}}))

        for item in results:
            item["_id"] = str(item["_id"])

        return make_response(status="success", message="Favorite stocks fetched", count=len(results), records=results)

    except Exception as e:
        return make_response(status="error", message=str(e))


@app.route("/api/favorites/funds", methods=["GET"])
def get_favorite_funds():
    try:
        user_id = request.args.get("userId")
        if not user_id:
            return make_response(status="error", message="userId required"), 400

        favs = list(favorites.find({"userId": user_id, "itemType": "fund"}))
        fund_ids = [f["itemId"] for f in favs]

        if not fund_ids:
            return make_response(status="success", message="No favorites", count=0, records=[])

        results = list(fund_holdings.find({"unique_id": {"$in": fund_ids}}))

        for r in results:
            r["_id"] = str(r["_id"])

        return make_response(status="success", message="Favorite funds fetched", count=len(results), records=results)

    except Exception as e:
        return make_response(status="error", message=str(e))


# --------------------------
# CORS HEADERS
# --------------------------
@app.after_request
def add_cors_headers(response):
    response.headers.setdefault("Access-Control-Allow-Origin", "http://localhost:4200")
    response.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.setdefault("Access-Control-Allow-Credentials", "true")
    return response


# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
