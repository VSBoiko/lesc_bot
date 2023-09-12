class MessagesText:
    @staticmethod
    def get_hello():
        return f"LESC - Local English speaking club BOT\nВсем хай!"

    @staticmethod
    def get_club_dates():
        return f"На какие даты будет клуб:"

    @staticmethod
    def get_date_and_time(datetime_str):
        return f"Дата и время: {datetime_str}"

    @staticmethod
    def get_place(place_str):
        return f"Место: {place_str}"

    @staticmethod
    def get_cnt_free_tickets(cnt_free_tickets):
        return f"Свободных мест - {cnt_free_tickets}"

    @staticmethod
    def get_no_tickets():
        return "Sorry, кажется, уже все места заняты, выбери другой день"

    @staticmethod
    def get_booking_success():
        return "Записали! Приходи не забывай плати деньги"

    @staticmethod
    def get_smt_went_wrong():
        return "Что то пошло не так, извините, попробуйте еще раз или напишите нам"

    @staticmethod
    def get_booking_already():
        return "Вы уже сделали бронь на это занятие, подвердите оплату и приходите!"
