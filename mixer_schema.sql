create table addresses (
    deposit_address_id      integer primary key autoincrement not null,
    destination_addresses   text,
    total_sent_to_mixer     integer not null default 0,
    total_sent_from_mixer   integer not null default 0
)
