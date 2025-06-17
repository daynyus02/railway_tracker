-- Drop tables in dependency order
DROP TABLE IF EXISTS operator_incident_assignment;
DROP TABLE IF EXISTS incident;
DROP TABLE IF EXISTS cancellation;
DROP TABLE IF EXISTS train_stop;
DROP TABLE IF EXISTS train_service;
DROP TABLE IF EXISTS route;
DROP TABLE IF EXISTS operator;
DROP TABLE IF EXISTS station;

CREATE TABLE station (
    station_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    station_name VARCHAR(50) NOT NULL,
    station_crs VARCHAR(3) NOT NULL,
    PRIMARY KEY (station_id)
);

CREATE TABLE operator (
    operator_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    operator_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (operator_id)
);

CREATE TABLE route (
    route_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    origin_station_id SMALLINT NOT NULL,
    destination_station_id SMALLINT NOT NULL,
    operator_id SMALLINT NOT NULL,
    PRIMARY KEY (route_id),
    FOREIGN KEY (operator_id) REFERENCES operator(operator_id),
    FOREIGN KEY (origin_station_id) REFERENCES station(station_id),
    FOREIGN KEY (destination_station_id) REFERENCES station(station_id)
);

CREATE TABLE train_service (
    train_service_id INT GENERATED ALWAYS AS IDENTITY,
    service_uid VARCHAR(6) NOT NULL,
    train_identity VARCHAR(4) NOT NULL,
    service_date DATE NOT NULL,
    route_id INT NOT NULL,
    PRIMARY KEY (train_service_id),
    FOREIGN KEY (route_id) REFERENCES route(route_id),
    UNIQUE (service_uid, service_date)
);

CREATE TABLE train_stop (
    train_stop_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    train_service_id INT NOT NULL,
    station_id SMALLINT NOT NULL,
    scheduled_arr_time TIME,
    actual_arr_time TIME,
    scheduled_dep_time TIME,
    actual_dep_time TIME,
    platform VARCHAR(3) NOT NULL,
    platform_changed BOOLEAN NOT NULL,
    PRIMARY KEY (train_stop_id),
    FOREIGN KEY (station_id) REFERENCES station(station_id),
    FOREIGN KEY (train_service_id) REFERENCES train_service(train_service_id)
    UNIQUE (train_service_id, station_id)
);

CREATE TABLE cancellation (
    cancellation_id INT GENERATED ALWAYS AS IDENTITY,
    train_stop_id INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    PRIMARY KEY (cancellation_id),
    FOREIGN KEY (train_stop_id) REFERENCES train_stop(train_stop_id)
);

CREATE TABLE incident (
    incident_id INT GENERATED ALWAYS AS IDENTITY,
    route_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    description TEXT NOT NULL,
    incident_number VARCHAR(32) NOT NULL,
    version_number BIGINT NOT NULL,
    is_planned BOOLEAN NOT NULL,
    info_link VARCHAR(255) NOT NULL,
    summary VARCHAR(255) NOT NULL,
    PRIMARY KEY (incident_id),
    FOREIGN KEY (route_id) REFERENCES route(route_id)
);

CREATE TABLE operator_incident_assignment (
    operator_incident_assignment_id INT GENERATED ALWAYS AS IDENTITY,
    incident_id INT NOT NULL,
    operator_id SMALLINT NOT NULL,
    PRIMARY KEY (operator_incident_assignment_id),
    FOREIGN KEY (incident_id) REFERENCES incident(incident_id),
    FOREIGN KEY (operator_id) REFERENCES operator(operator_id)
);
