SHELL := /bin/bash

run_test:
	VERBOSE=true OUT=../csv2 ASSETS=btc,eth,sol THROTTLE=true node node/generate.js

run_test_large:
	VERBOSE=true OUT=../csv2 THROTTLE=true node node/generate.js

create_csv:
	python python/create_csv.py

copy_csv_to_postgres:
	docker exec coinmetrics-data-backup_db_1 psql -h localhost -U cm_data -d cm_data -c "\copy public.all_coins FROM /all_coin_data/all_coin_data.csv with (format csv,header true, delimiter ',');"

delete_records_all_coins:
	docker exec coinmetrics-data-backup_db_1 psql -h localhost -U cm_data -d cm_data -c "delete from all_coins;"

create_all_coins_table:
	docker exec coinmetrics-data-backup_db_1 psql -h localhost -U cm_data -d cm_data -f /sql/create_all_coins.sql

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
