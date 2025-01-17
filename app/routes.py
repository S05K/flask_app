from flask import Response, json, jsonify
from .models import ROLE_CHOICES, User, PlayerDetail, OwnerDetail
from flask_restful import Resource
from . import api
from . import app
from flask import request
from . import bcrypt
from utils.utils import make_response, validate_owner_data
from . import db, mail
from flask_mail import Message
from utils.utils import validate_user_data
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, set_access_cookies, decode_token,
    jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies, verify_jwt_in_request, exceptions as jwt_exceptions
)
from flask import render_template
from tasks import send_email

@app.route("/")
def home():
    return render_template("index.html")

class PlayerView(Resource):
    def post(self):
        try:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            role = 'player'
            password = data.get('password')
            skill = data.get('skill')
            highest_score = data.get('highest_score', None)
            highest_wicket = data.get('highest_wicket', None)
            total_innings =data.get('total_innings', None)
            strike_rate = data.get('strike_rate', None)
            not_out = data.get('not_out', None)

            validation_error = validate_user_data(data)
            if validation_error:
                return make_response("Error",data={"user": validation_error}, status_code=400)
            else:
                user = User(
                        name = name,
                        email = email,
                        role = role,
                        password = bcrypt.generate_password_hash(
                        password).decode('utf-8')
                    )
                db.session.add(user)
                db.session.commit()
                player_detail = PlayerDetail(
                    skill = skill,
                    highest_score = highest_score,
                    highest_wicket = highest_wicket,
                    total_innings = total_innings,
                    strike_rate = strike_rate,
                    not_out = not_out,
                    user_id = user.id,
                )
                player_detail.price = player_detail.calculate_price()
                db.session.add(player_detail)
                db.session.commit()
                return make_response("success", "Player created successfully", data={"user": user.to_dict()}, status_code=201)
        except Exception as e:
            return make_response("Failed", "Error", data={"error": e}, status_code=400)



class OwnerRegisterView(Resource):
    def post(self):
        try:
            data = request.get_json()
            name = data.get('name',None)
            email = data.get('email',None)
            role = 'owner'
            money = 100000
            password = data.get('password',None)
            team_name = data.get('team_name')
            
            validation_error = validate_user_data(data)
            print(validation_error)
            validate_owner = validate_owner_data(data)
            
            if validation_error:
                return make_response("Error",data={"user": validation_error}, status_code=400)
            if validate_owner:
                return make_response("Error",data={"owner": validate_owner}, status_code=400)
            else:
                user = User(
                        name = name,
                        email = email,
                        role = role,
                        password = bcrypt.generate_password_hash(
                        password).decode('utf-8')
                    )
                db.session.add(user)
                db.session.commit()
                
                owner_detail = OwnerDetail(
                    user_id = user.id, 
                    team_name=team_name,
                    money = money
                )
                db.session.add(owner_detail)
                db.session.commit()
                return make_response("success", "Owner created successfully", data={"user": user.to_dict()}, status_code=201)
        except Exception as e:
            return make_response("Failed", "Error", data={"error": e}, status_code=400)



    
class LoginView(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email', None)
            password = data.get('password', None)

            user = User.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                return make_response("success", "Login successfully", data={"access_token": access_token, "refresh_token":refresh_token}, status_code=200)
            else:
                return make_response("Failed", "Not Found",status_code=404)
        except Exception as e:
            return make_response("Failed", "Error", data={"error": e}, status_code=400)


class HomeView(Resource):
    @jwt_required()
    def get(self):
        print("---------------------------------")
        current_user = get_jwt_identity()
        print(current_user)
        user = User.query.filter_by(id=current_user).first()
        player = PlayerDetail.query.all()
        print(player)
        if user.is_owner():
            owner = user.owner_detail
            owner_data = {'owner_id':owner[0].id, 'money':owner[0].money, 'purchased_player_ids':owner[0].player_ids, 'team_name':owner[0].team_name}
            return make_response("success", "Logged-in",data={"your_data":owner_data}, status_code=200)
        else:
            return Response(json.dumps({'message': 'user not found'}), status=404, content_type="application/json")
        

class OwnerView(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        print(current_user)
        user = User.query.filter_by(id=current_user).first()
        if user.is_owner():
            print("yesss")
            players = PlayerDetail.query.all()
            # all_players = [player.to_dict() for player in players]
            new_list = list()
            for i in players:
                new_list.append(i.to_dict())
            # print(new_list)
            return make_response("success", "Logged-in", data={"players":new_list},status_code=200)
        else:
            return make_response("Error", "Not a owner", status_code=400)   

class PlayerFilterApi(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        first_data = data.get('price_from')
        second_data = data.get('price_to')
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user).first()
        if user.is_owner():
            total_players = PlayerDetail.query.filter(PlayerDetail.price.between(first_data,second_data)).order_by(PlayerDetail.price.asc()).all()
            if total_players:
                players = [i.to_dict() for i in total_players]
                return make_response("success", "Logged-in", data={"players":players},status_code=200)
            else:
                player = PlayerDetail.query.all()
                return make_response("success", "There is no player for your range please select another range", status_code=404)
        else:
            return make_response("Error", "Not a owner", status_code=400)

class PurchasePlayerApi(Resource):
    @jwt_required()
    def put(self):
        # breakpoint()
        data = request.get_json()
        player_ids = data.get("player_ids")
        player = PlayerDetail.query.filter_by(id=player_ids).first()
        if not player:
            return make_response("Failed", "Error", data={"error": "Player not found"}, status_code=404)
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user).first()
        player = PlayerDetail.query.filter_by(id=player_ids).first()
        email = player.user.email if player else None
        check_player_is_available = PlayerDetail.query.filter_by(id=player_ids).first()
        if check_player_is_available.is_sold:          
            return make_response("Can't Purchase", "Player is already sold", status_code=200)
        else:
            if user.is_owner():
                owner = user.owner_detail
                owner_id = owner[0].id
                player_purchasing = OwnerDetail.query.filter_by(id=owner_id).first()
                player_purchasing.player_ids.append(player_ids)
                if player.price>player_purchasing.money:
                    return make_response("Can't Purchase", "You have not enough money", status_code=200)
                player_purchasing.money = player_purchasing.money - player.price
                db.session.add(player_purchasing)
                db.session.commit()

                player = PlayerDetail.query.filter_by(id=player_ids).first()
                player.is_sold = True
                db.session.add(player)
                db.session.commit()

                send_email.delay(email,user.email,user.name)
                return make_response("success", "Player is purchased", data={"price":player.price},status_code=200)


api.add_resource(PlayerView, '/player-registration', methods=['POST'])
api.add_resource(OwnerRegisterView, "/owner-registration", methods= ['POST'])
api.add_resource(LoginView,"/login",methods=['POST'])
api.add_resource(HomeView,"/home", methods=['GET'])
api.add_resource(OwnerView,"/player",methods=['GET','POST'])
api.add_resource(PlayerFilterApi, "/players/filter", methods = ['POST'])
api.add_resource(PurchasePlayerApi, "/purchase-player", methods=['PUT'])

