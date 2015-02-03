import sqlalchemy as sa

DB = 'postgresql://howmuchsnow:howmuchsnow@localhost/howmuchsnow_test'

def how_much_snow_gps (user_loc, conn):
    '''Takes a tuple of a user's estimated latitude and longitude, and a
    database connection. From the database, gets all rows for the nearest
    three points to the user. Groups the data by the hour the snowfall is
    predicted for. Interpolates at each hour to get a predicted amount of
    snow. Returns the max predicted amount of snow.'''
    inches_of_snow = get_from_db (user_loc, conn)
    return format_amount(inches_of_snow)

def get_from_db ((latitude, longitude), conn):
    '''Given user coordinates and a database connection, get the weighted average
    by distance squared of all of the nearby stations. Returns amount of snow in inches.
    '''
    query = sa.text('''
        select
            sum(influence * msnow) / sum (influence) * 39.3701
        from (
            select
                1 / distance(latitude, longitude, :lat, :lon)^2 influence,
                sum ( metersofsnow ) msnow
            from
                prediction
            join
                location on location.id = prediction.locationid
            where
                distance(latitude, longitude, :lat, :lon) < 50
            group by
                latitude,
                longitude
            ) aggregate
    ''')
    (result,) = conn.execute(query, lat = latitude, lon = longitude).first()
    return result

def format_amount(inches):
    reported_value = int(round(inches))
    unit = unit_word(reported_value)
    return str(reported_value) + ' ' + unit

def unit_word (inches):
    if inches == 1:
        return "inch"
    else:
        return "inches"

def make_coordinates(lat, lon):
    return '''Assuming you're near <a
        href="https://www.google.com/maps?q={0}%2C{1}">{0}&deg;N
        {1}&deg;W</a> | '''.format(lat, lon)
