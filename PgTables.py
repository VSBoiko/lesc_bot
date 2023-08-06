class PgTables:
    def __init__(self, db):
        self.db = db

    def create(self):
        self._create_tg_users()
        self._create_places()
        self._create_meetings()
        self._create_tickets()
        self._create_bookings()

    def _create_tg_users(self):
        # таблица "Пользователи"
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tg_users
            (
                id      serial,
                tg_id   bigint,
                login   varchar(100) DEFAULT '',
                name_   varchar(100) DEFAULT '',
                surname varchar(100) DEFAULT '',
                PRIMARY KEY (id)
            );
        """)

    def _create_meetings(self):
        # таблица "Встречи"
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS meetings
            (
                id        serial,
                place_id  int,
                date_time timestamp,
                name_     varchar(500) DEFAULT '',
                primary key (id),
                constraint fk_place
                    foreign key (place_id)
                        references places (id)
            );
        """)

    def _create_places(self):
        # таблица "Места встреч"
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS places
            (
                id          serial,
                name_       varchar(500),
                address     varchar(500),
                link        varchar(500)  DEFAULT '',
                description varchar(1000) DEFAULT '',
                PRIMARY KEY (id)
            );
        """)

    def _create_tickets(self):
        # таблица "Билеты"
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tickets
            (
                id         serial,
                meeting_id int,
                price      money,
                primary key (id),
                constraint fk_meeting
                    foreign key (meeting_id)
                        references meetings (id)
            
            );
        """)

    def _create_bookings(self):
        # таблица "Бронирования"
        self.db.execute("""
            create table if not exists bookings
            (
                id        serial,
                ticket_id int,
                user_id   int,
                is_paid   bool      default False,
                date_time timestamp default current_timestamp,
                primary key (id),
                constraint fk_ticket
                    foreign key (ticket_id)
                        references tickets (id),
                constraint fk_user
                    foreign key (user_id)
                        references tg_users (id)
            );
        """)
