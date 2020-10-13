select * from processostf_lote_linha;
select * from processostf_lote;

insert into processostf_lote_linha (id_lote,status,data_cad, apagado, user_cad, processo)
values (
1,
1,
now(),
0,
'a.batista',
'00049233920071000000'
)

00087377820151000000
00049233920071000000



insert into processostf_lote (nome_lote, status, data_cad, apagado, user_cad) values (
'Lote training',
1,
now(),
0,
'a.batista'
)