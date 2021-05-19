select * from processostf_lote_linha;
select * from processostf_lote;

update processostf_lote set status = 1 where id_lote = 1

update processostf_lote set status = 4
update processostf_lote_linha set status = 1 where id_linha = 3

select * from tbl_andamentos
select * from tbl_decisoes

truncate table tbl_andamentos;
truncate table tbl_decisoes;
truncate table tbl_partes;


select * from tbl_partes
select * from status
select * from tbl_log_erros

 select 
                id_lote, 
                nome_lote, 
                status, 
                data_cad, 
                data_fim, 
                user_cad 
            from 
                processostf_lote
            where
                apagado = 0
                and status = 12
            order by data_cad 
            limit(1) 

update processostf_lote_linha set data_inicio_processamento = null

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

select * from status