class Messages:
    @staticmethod
    def hello():
        return f"LESC - Local English speaking club BOT\nВсем хай!"

    @staticmethod
    def meetings_dates():
        return f"На какие даты будет клуб:"

    @staticmethod
    def meeting_dates_after_cancel():
        return "Бронирование отменено, посмотри встречи на другую дату"

    @staticmethod
    def meeting_date_and_time(datetime_str):
        return f"Дата и время: {datetime_str}"

    @staticmethod
    def meeting_place(place_str):
        return f"Место встречи - {place_str}"

    @staticmethod
    def cnt_free_tickets(cnt_free_tickets):
        return f"Свободных мест - {cnt_free_tickets}"

    @staticmethod
    def no_free_tickets():
        return "Sorry, кажется, уже все места заняты, выбери другой день"

    @staticmethod
    def no_member_ticket():
        return "Вы еще не забронировали место на эту встречу, вернитесь плис на меню со встречей и забронируйте снова"

    @staticmethod
    def no_meetings():
        return "Мы готовим ближайшие встречи и скоро вы сможете записаться на них"

    @staticmethod
    def no_meetings_after_cancel():
        return "Бронирование отменено, готовим ближайшие встречи и скоро вы сможете записаться на них"

    @staticmethod
    def booking_success():
        return "Вы забронировали место на эту встречу!"

    @staticmethod
    def booking_success_pay_confirm():
        return "Мы проверяем оплату, если сейчас ночь, то мы подтвердим бронирование утром, не волнуйтесь, мы вас ждем"

    @staticmethod
    def booking_success_pay_success():
        return "Мы подтвердили вашу оплату, спасибо, ждем вас на встрече!"

    @staticmethod
    def booking_already():
        return "Вы уже сделали бронь на это занятие, подтвердите оплату и приходите!"

    @staticmethod
    def booking_unavailable():
        return "Бронирований на эту встречу пока что не доступны, мы откроем запись чуть позже"

    @staticmethod
    def payment_info():
        return "Оплатите его по номер +7 (800) 555-35-35 (Соня Батьковна А.) на Сбербанк / Тинькофф и подтвердите перевод по кнопке 'Подтвердить'"

    @staticmethod
    def cancel_in_meeting_day():
        return "Вы отменяете бронирование в день встречи, по нашим правилам мы не можем вам вернуть деньги( Вы уверены, что хотите отменить бронирование?"

    @staticmethod
    def cancel_already():
        return "Похоже, что то вы уже отменили бронирование на эту встречу"

    @staticmethod
    def cancel_with_return_money():
        return "Бронирование отменено, сейчас вернем деньги, посмотри встречи на другую дату"

    @staticmethod
    def cancel_with_return_success():
        return "Мы отменили вашу бронь и вернули деньги, увидимся на другой встрече, выберите для себя подходящую"

    @staticmethod
    def cancel_by_admin():
        return "Мы не подтвердили ваше бронирование, увидимся на другой встрече, если вы платили деньги, то мы их вам уже вернули"

    @staticmethod
    def cancel_with_return_no_money():
        return "Бронирование отменено, деньги не вернем потому что вы отменили встречу в день встречи, посмотрите встречи на другую дату"


