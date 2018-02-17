create table deposit_addresses (
    deposit_address_id      integer primary key autoincrement not null,
    total_sent_to_mixer     text not null default '0.0',
    total_sent_from_mixer   text not null default '0.0'
);

create table destination_addresses (
    deposit_address_id  integer not null,
    destination_address text not null unique
);
