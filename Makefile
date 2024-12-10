SHELL := /bin/bash

run_test:
	VERBOSE=true OUT=./csv2 ASSETS=btc,eth,sol THROTTLE=true node node/generate.js

run_test_no_throttle:
	VERBOSE=true OUT=./csv2 ASSETS=btc,eth,sol node node/generate.js

run_test_large:
	VERBOSE=true OUT=./csv2 THROTTLE=true node node/generate.js

create_csv:
	python python/create_csv.py

copy_csv_to_postgres:
	PGPASSWORD=cm_data psql -h localhost -p 5433 -U cm_data -d cm_data -c "\copy public.all_coins FROM all_coin_data/all_coin_data.csv with (format csv,header true, delimiter ',');"

delete_records_all_coins:
	PGPASSWORD=cm_data psql -h localhost -p 5433 -U cm_data -d cm_data -c "delete from all_coins;"

delete_records_update_table:
	PGPASSWORD=cm_data psql -h localhost -p 5433 -U cm_data -d cm_data -c "delete from update_table;"

create_all_coins_table:
	PGPASSWORD=cm_data psql -h localhost -p 5433 -U cm_data -d cm_data -f sql/create_all_coins.sql

update_all_coins:
	PGPASSWORD=cm_data psql -h localhost -p 5433 -U cm_data -d cm_data -f sql/update_all_coins.sql

up:
	docker-compose -f docker-compose.yml up

kill:
	docker-compose kill

start:
	docker-compose start

stop:
	docker-compose stop

restart: stop start

docker_shell:
	docker exec -it coinmetrics-data-backup_db_1 bash

temp_file_load:
	python python/temp_file_load.py

gen_py:
	python python/generate.py

make_update_table: delete_records_update_table temp_file_load

update_table_and_all_coins: make_update_table update_all_coins

rm_temp_dir:
	find csv3/ -name "*.csv" -exec rm {} \;

run_update_process: rm_temp_dir gen_py update_table_and_all_coins
