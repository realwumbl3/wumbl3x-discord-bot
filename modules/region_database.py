import logging
from datetime import datetime
import json
import requests
from zyXserve.v1_3.Sqlite import SqliteDatabase, orm, sql

visits_database = SqliteDatabase({"db_path": f"db/visits.db", "overwrite": False})


class VisitCountry(visits_database.base):
    __tablename__ = "visit_country"
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(255))

    visits = orm.relationship("Visit", back_populates="country")
    visit_count = sql.Column(sql.Integer, default=0)

    regions = orm.relationship("VisitRegion", back_populates="country")


class VisitRegion(visits_database.base):
    __tablename__ = "visit_region"
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(255))

    visits = orm.relationship("Visit", back_populates="region")
    visit_count = sql.Column(sql.Integer, default=0)

    country_id = sql.Column(sql.Integer, sql.ForeignKey("visit_country.id"))
    country = orm.relationship("VisitCountry", back_populates="regions")
    cities = orm.relationship("VisitCity", back_populates="region")


class VisitCity(visits_database.base):
    __tablename__ = "visit_city"
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(255))

    visits = orm.relationship("Visit", back_populates="city")
    visit_count = sql.Column(sql.Integer, default=0)

    region_id = sql.Column(sql.Integer, sql.ForeignKey("visit_region.id"))
    region = orm.relationship("VisitRegion", back_populates="cities")


class Visit(visits_database.base):
    __tablename__ = "visit"
    id = sql.Column(sql.Integer, primary_key=True)
    created_at = sql.Column(sql.DateTime, default=datetime.utcnow)
    ip = sql.Column(sql.String(255))

    country_id = sql.Column(sql.Integer, sql.ForeignKey("visit_country.id"))
    country = orm.relationship("VisitCountry", back_populates="visits")

    region_id = sql.Column(sql.Integer, sql.ForeignKey("visit_region.id"))
    region = orm.relationship("VisitRegion", back_populates="visits")

    city_id = sql.Column(sql.Integer, sql.ForeignKey("visit_city.id"))
    city = orm.relationship("VisitCity", back_populates="visits")


visits_database.create_all()


def get_location_database_entries(session, country, region, city):
    db_country = session.query(VisitCountry).filter_by(name=country).first()
    if db_country is None:
        db_country = VisitCountry(name=country)
        session.add(db_country)
    db_region = session.query(VisitRegion).filter_by(name=region).first()
    if db_region is None:
        db_region = VisitRegion(name=region)
        db_country.regions.append(db_region)
        session.add(db_region)
    db_city = session.query(VisitCity).filter_by(name=city).first()
    if db_city is None:
        db_city = VisitCity(name=city)
        db_region.cities.append(db_city)
        session.add(db_city)
    session.commit()
    return db_country, db_region, db_city


# function to get user's country of origin from IP address
def get_visitor_data(request):
    try:
        session = visits_database.session()
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        response = requests.get("http://ip-api.com/json/" + ip)
        json_response = response.json()
        country = json_response["country"]
        region = json_response["regionName"]
        city = json_response["city"]

        db_country, db_region, db_city = get_location_database_entries(
            session, country, region, city
        )

        db_visit = Visit(ip=ip, country=db_country, region=db_region, city=db_city)

        db_city.visit_count += 1
        db_country.visit_count += 1
        db_region.visit_count += 1

        session.add(db_visit)

    except Exception as e:
        logging.exception(e)
        session.rollback()
    finally:
        session.commit()
