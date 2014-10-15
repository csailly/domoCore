alter table histo_temp add sonde INTEGER;
update histo_temp set sonde = 1 where sonde is null;