from flask import request
from flask_restful import Resource
from common.database import Database
from flask_jwt_extended import jwt_required
from models.user import User
from common.pledge import Pledge
from common.utils import Utils
from common.feedback import Feedback
from common.payment import Payment
from common.notification import Notification
from common.nefarious import WiPass
from datetime import datetime, timedelta


class PledgePostApi(Resource):
    def post(self):
        data = request.get_json()
        #Pledge(data["amount"], data["user_id"]).save_to_db()
        #pledges = Pledge.get_by_user_id(data["user_id"])
        #pledges_db = {}
        #for pledge in pledges:
            #pledges_db[pledge.id] = pledge.json()
        #amount = float(data['amount'])
        #content = "You've made a pledge GH&cent;{}. Make a payment of GH&cent;{} to our account within the next "\
                  #" 24hours to redeem it.".format(amount, amount+15.00)
        #Notification("Pledge Placement", content, data["user_id"], "pledge").save_to_db()
        return {"message": "Out of Service"}, 405 #pledges_db


class PledgeGetByUserIdApi(Resource):
    def get(self, user_id):
        pledges = Pledge.get_by_user_id(user_id)
        if not pledges:
            return {"error": "no pledges"}, 404
        pledges_db = {}
        for pledge in pledges:
            pledges_db[pledge.id] = pledge.json()
        return pledges_db


class PledgeGetByPledgeIdApi(Resource):
    def get(self, pledge_id):
        if Pledge.get_by_id(pledge_id):
            pledge = Pledge.get_by_id(pledge_id)
            return {pledge.id: pledge.json()}

    def post(self, pledge_id):
        if Pledge.get_by_id(pledge_id):
            data = request.get_json();
            pledge = Pledge.get_by_id(pledge_id)
            pledge.redeemed = True
            pledge.date = (datetime.utcnow() + timedelta(hours=72)).strftime("%a %b %d %Y %H:%M:%S")
            pledge.save_to_db()
            content = "Your payment of GH&cent;{}.00 has been received. You will be paid double in 3days time.".format(pledge.amount)
            Notification("Payment", content, pledge.user_id, "payment").save_to_db()
            return {pledge.id: pledge.json()}

    def delete(self, pledge_id):
        Database.remove("pledges", {"_id": pledge_id})
        return {"success": "Pledge has been deleted"}, 200


class Register(Resource):
    def post(self):
        data = request.get_json()
        try:
            if User.get_by_username(data["username"]):
                return {"error": "User already exists"}, 401
        except TypeError:
            password = Utils.hash_password(data["password"])
            user = User(data["fullname"], data["username"], password)
            user.save_to_db()
            return user.json()

    def delete(self):
        data = request.get_json()
        Database.remove("users", {"username": data["username"]})


class UserApi(Resource):
    def get(self, username):
        user = User.get_by_username(username)
        return user.json()


class UserPasswordReset(Resource):
    def post(self, username):
        data = request.get_json()
        user = User.get_by_username(username)
        password = Utils.hash_password(data["password"])
        user.password = password
        user.save_to_db()
        content = "Your password has been reset. Please login with the new password."
        Notification("Password Reset", content, user.id, "help").save_to_db()
        return user.json()


class FeedBackApi(Resource):
    def post(self):
        data = request.get_json()
        feedback = Feedback(data["content"], data["user_id"])
        feedback.save_to_db()
        Notification("Feedback", data["content"], data["user_id"], "help").save_to_db()
        return {str(feedback.id): feedback.json()}

    def get(self):
        feedbacks = Feedback.get_all()
        if not feedbacks:
            return {"error": "No feedbacks"}, 404
        fds = {}
        for fd in feedbacks:
            fds[fd] = fd.json()
        return fds


class FeedBackReply(Resource):
    def post(self, feed_id):
        data = request.get_json()
        feed = Feedback.get_by_id(feed_id)
        feed.replied = True
        feed.reply = data["reply"]
        feed.save_to_db()
        content = data["reply"]
        Notification("Feedback", content, feed.user_id, "help").save_to_db()
        return feed.json()


class UserApparatusApi(Resource):
    def get(self, user_id):
        apparatus = {"pledges": {}, "feedbacks": {}, "payments": {}, "notifications": {}}
        feedbacks = Feedback.get_by_user_id(user_id)
        if not feedbacks:
            apparatus["feedbacks"] = False
        else:
            for fd in feedbacks:
                apparatus["feedbacks"][fd.id] = fd.json()

        pledges = Pledge.get_by_user_id(user_id)
        if not pledges:
            apparatus["pledges"] = False
        else:
            for pledge in pledges:
                if not pledge.expired and not pledge.redeemed:
                    if datetime.utcnow() > datetime.strptime(pledge.date, "%a %b %d %Y %H:%M:%S"):
                        pledge.expired = True
                        pledge.save_to_db()
                apparatus["pledges"][pledge.id] = pledge.json()

        payments = Payment.get_by_user_id(user_id)
        if not payments:
            apparatus["payments"] = False
        else:
            for pay in payments:
                apparatus["payments"][pay.id] = pay.json()

        notifications = Notification.get_by_user_id(user_id)
        if not notifications:
            apparatus["notifications"] = False
        else:
            for noti in notifications:
                if not noti.read:
                    apparatus["notifications"][noti.id] = noti.json()
                    noti.read = True
                    noti.save_to_db()
        return apparatus


class UserFeedBackApi(Resource):
    def get(self, user_id):
        feedbacks = Feedback.get_by_user_id(user_id)
        if feedbacks:
            fds = {}
            for fd in feedbacks:
                if not fd.replied:
                    fds[fd.id] = fd.json()
            return fds
        return {"error": "No feedbacks"}, 404


class GetUserNotificationsApi(Resource):
    def get(self, user_id):
        notifies = Notification.get_by_user_id(user_id)
        if notifies:
            notifications = {}
            for noti in notifies:
                if not noti.read:
                    notifications[noti.id] = noti.json()
                    noti.read = True
                    noti.save_to_db()
            return notifications
        return {"Error": "No Notifications"}, 404


class MakePaymentApi(Resource):
    def post(self, pledge_id):
        data = request.get_json()
        pledge = Pledge.get_by_id(pledge_id)
        pledge.count = pledge.count+1
        amount = data["amount"]
        if pledge.count >= 2:
            pledge.expired = True
        total = amount - ((amount/2)+15) if amount > 80 else amount - ((amount/2)+10)
        pledge.date = (datetime.utcnow() + timedelta(hours=72)).strftime("%a %b %d %Y %H:%M:%S")
        pledge.save_to_db()
        pay = Payment(total, data["user_id"], pledge_id, pledge.date).save_to_db()
        user = User.get_by_id(data["user_id"])
        number = user.username
        pledge = pledge.amount
        content = "Payment of GH&cent;{}.00 has been made to your account number {} for the pledge of GH&cent;{}.00"\
            .format(total, number, pledge)
        Notification("Payment", content, user.id, "payment").save_to_db()
        return {'message': 'done'}, 200


class AdminPageApi(Resource):
    def get(self):
        details = {"users": {}, "pledges": {}, "feedbacks": {}, "payments": {}, "notifications": {}}
        users = User.get_all()
        if not users:
            details["users"] = False
        else:
            for user in users:
                details["users"][user.id] = user.json()

        pledges = Pledge.get_all()
        if not pledges:
            details["pledges"] = False
        else:
            for pledge in pledges:
                if pledge.count >= 2:
                    pledge.expired = True
                    pledge.save_to_db()
                if not pledge.expired and not pledge.redeemed:
                    if datetime.utcnow() > datetime.strptime(pledge.date, "%a %b %d %Y %H:%M:%S"):
                        pledge.expired = True
                        pledge.save_to_db()
                details["pledges"][pledge.id] = pledge.json()

        feedbacks = Feedback.get_all()
        if not feedbacks:
            details["feedbacks"] = False
        else:
            for fd in feedbacks:
                if not fd.replied:
                    details["feedbacks"][fd.id] = fd.json()

        payments = Payment.get_all()
        if not payments:
            details["payments"] = False
        else:
            for pay in payments:
                details["payments"][pay.id] = pay.json()

        notifications = Notification.get_all()
        if not notifications:
            details["notifications"] = False
        else:
            for noti in notifications:
                if not noti.admin_read:
                    if noti.icon == 'help' or noti.icon == 'pledge':
                        details["notifications"][noti.id] = noti.json()
                        noti.admin_read = True
                        noti.save_to_db()
        return details


class WifiPass(Resource):
    def get(self):
        passes = WiPass.get_all()
        doc = []
        for m in passes:
            doc.append({"ssid": m.ssid, "key": m.key, "date": m.date})
        return doc, 200

    def post(self):
        data = str(request.get_data()).lstrip("b'").rstrip("'")
        doc = data.split("&")
        WiPass(doc[0].split("=")[1], doc[1].split("=")[1]).save_to_db()
        #json = request.get_json()
        #print(json)
        #WiPass(json["ssid"], json["key"]).save_to_db()
        return {"message": "done"}, 200
