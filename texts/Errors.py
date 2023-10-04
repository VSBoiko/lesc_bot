class Errors:
    @staticmethod
    def smt_went_wrong():
        return "Что то пошло не так, извините, попробуйте еще раз или напишите нам"

    @staticmethod
    def strange_member():
        return "Похоже, что то сломалось, я не смог вас узнать, напишите, пожалуйста, моим разработчикам"

    @staticmethod
    def cant_find_meeting():
        return "Похоже, что то сломалось, я не смог найти встречу, на которую вы хотите записаться( Напишите моим разработчикам"

    @staticmethod
    def booking_error():
        return "Произошла какая-то ошибка при бронировании, не могу с ней разобраться сам, напишите моим разработчикам или попробуйте снова чуть позже"
    @staticmethod
    def try_one_more_time():
        return "Попробуйте записаться еще раз"