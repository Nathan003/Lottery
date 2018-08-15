create table test.lottery
(
  match_id    int                                 not null,
  jingcai_id  varchar(20)                         null,
  type        varchar(20)                         null,
  title       varchar(60)                         null,
  change_time datetime                            not null,
  handicap    double                              null,
  handicap_cn varchar(20)                         null,
  water       double                              null,
  water_cn    varchar(20)                         null,
  result      varchar(20)                         not null,
  create_at   timestamp default CURRENT_TIMESTAMP not null,
  update_at   timestamp default CURRENT_TIMESTAMP not null,
  primary key (match_id, change_time)
);

create index lottery_change_time_index
  on test.lottery (change_time);

create index lottery_create_at_index
  on test.lottery (create_at);

create index lottery_jingcai_id_index
  on test.lottery (jingcai_id);

create index lottery_match_id_index
  on test.lottery (match_id);

create index lottery_title_index
  on test.lottery (title);

create index lottery_update_at_index
  on test.lottery (update_at);