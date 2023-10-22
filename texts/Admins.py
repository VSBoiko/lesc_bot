class Admins:
    @staticmethod
    def confirm_pay(user_info: str, meeting_info: str):
        return f"{user_info} говорит, что оплатил встречу {meeting_info}, подтвердите оплату"

    @staticmethod
    def confirm_pay_subs(user_info: str):
        return f"{user_info} говорит, что оплатил абонемент, подтвердите оплату"

    @staticmethod
    def confirm_cancel(user_info: str, meeting_info: str):
        return f"{user_info} отменил запись на встречу {meeting_info}\n\nНадо вернуть ему деньги"

    @staticmethod
    def booking_success():
        return "Бронь подтвердил, участника оповестил, что все оплачено и все ок"

    @staticmethod
    def booking_cancel_success():
        return "Бронь отменили, участника оповестил, что бабки вернули и все ок"

    @staticmethod
    def booking_cancel_success_check_money():
        return "Бронь отменили, участника оповестил, проверьте платил он бабки или нет, а то я хз"

    @staticmethod
    def subscribe_success():
        return "Абонемент подтвердил, участника оповестил, что абонемент куплен и все ок"

    @staticmethod
    def subscribe_cancel_success():
        return "Абонемент отменил, участника оповестил, что бабки вернули и все ок"

    @staticmethod
    def subscribe_cancel_success_check_money():
        return "Абонемент отменил, участника оповестил, проверьте платил он бабки или нет, а то я хз"



    @staticmethod
    def cancel_already(what: str):
        return f"Похоже, что пользователь отменил {what}, ну и ладно"


    @staticmethod
    def error():
        return "Что по пошло не так и поломалось я хз"
