from flask import Flask, request, render_template, Response, redirect, flash, url_for, session, make_response, jsonify
app = Flask(__name__)
import requests
import json

app.secret_key = 'cs571hw6'

def basic_info():
    img_url = 'https://image.tmdb.org/t/p/w500'
    api_key = '?api_key=9152d19da914b763bbea03feeaebd8b0'
    
    trending_url = 'https://api.themoviedb.org/3/trending/movie/week' + api_key
    trending_r = requests.get(trending_url)
    trending_info = trending_r.json()['results']
    # app.logger.debug(len(trending_info))
    
    tv_url = 'https://api.themoviedb.org/3/tv/airing_today' + api_key
    tv_r = requests.get(tv_url)
    tv_info = tv_r.json()['results']

    trending_titles = []
    trending_backdrop_paths = []
    release_dates = []

    tv_titles = []
    tv_backdrop_paths = []
    first_air_dates = []
    
    for i in range(5): 
        trending_titles.append(trending_info[i]['title'])
        if trending_info[i]['backdrop_path'] == None:
            trending_backdrop_paths.append('https://bytes.usc.edu/cs571/s21_JSwasm00/hw/HW6/imgs/movie-placeholder.jpg')
        else:
            trending_backdrop_paths.append(img_url + trending_info[i]['backdrop_path'])
        release_dates.append(trending_info[i]['release_date'])
        tv_titles.append(tv_info[i]['name'])
        tv_backdrop_paths.append(img_url + tv_info[i]['backdrop_path'])
        first_air_dates.append(tv_info[i]['first_air_date'])
    return [trending_titles, trending_backdrop_paths, release_dates, tv_titles, tv_backdrop_paths, first_air_dates]

@app.route('/', methods=['GET'])  
def home():
    app.logger.debug('home')
    data = basic_info()
    dummy = []
    for i in range(10):
        dummy.append([])
    return render_template('home.html', trending_titles=data[0], trending_backdrops=data[1], dates=data[2], tv_titles=data[3], tv_backdrops=data[4], air_dates=data[5], search_ids=dummy, search_titles=dummy, search_overviews=dummy, search_posters=dummy, search_dates=dummy, search_avgs=dummy, search_cnts=dummy, search_genres=dummy, search='false', search_types=dummy)
    # return Response(200)

@app.route('/', methods=['POST'])
def search_data():
    app.logger.debug('search')
    data = basic_info()
    keyword = request.form['keyword']
    category = request.form['category']

    no_result = False

    movie_results = []
    tv_results = []
    if category == 'movie':
        movie_results = search_movie(keyword)[0:10]
        # app.logger.debug('movie_results:')
        # app.logger.debug(movie_results)
        if movie_results == []:
            data = basic_info()
            dummy = []
            for i in range(10):
                dummy.append([])
            return render_template('home.html', trending_titles=data[0], trending_backdrops=data[1], dates=data[2], tv_titles=data[3], tv_backdrops=data[4], air_dates=data[5], search_ids=dummy, search_titles=dummy, search_overviews=dummy, search_posters=dummy, search_dates=dummy, search_avgs=dummy, search_cnts=dummy, search_genres=dummy, search='no_result', search_types=dummy)
    elif category == 'tv':
        tv_results = search_tv(keyword)[0:10]
        if tv_results == []:
            data = basic_info()
            dummy = []
            for i in range(10):
                dummy.append([])
            return render_template('home.html', trending_titles=data[0], trending_backdrops=data[1], dates=data[2], tv_titles=data[3], tv_backdrops=data[4], air_dates=data[5], search_ids=dummy, search_titles=dummy, search_overviews=dummy, search_posters=dummy, search_dates=dummy, search_avgs=dummy, search_cnts=dummy, search_genres=dummy, search='no_result', search_types=dummy)
    elif category == 'both':
        movie_results = search_movie(keyword)
        tv_results = search_tv(keyword)
        movie_len = len(movie_results)
        tv_len = len(tv_results)
        if movie_results == [] and tv_results == []:
            data = basic_info()
            dummy = []
            for i in range(10):
                dummy.append([])
            return render_template('home.html', trending_titles=data[0], trending_backdrops=data[1], dates=data[2], tv_titles=data[3], tv_backdrops=data[4], air_dates=data[5], search_ids=dummy, search_titles=dummy, search_overviews=dummy, search_posters=dummy, search_dates=dummy, search_avgs=dummy, search_cnts=dummy, search_genres=dummy, search='no_result', search_types=dummy)
        elif movie_len < 5:
            if tv_len < 10 - movie_len:
                pass
            else:
                tv_results = tv_results[0:(10-movie_len)]
        elif tv_len < 5:
            if movie_len < 10 - tv_len:
                pass
            else:
                movie_results = movie_results[0:(10-movie_len)]
        else:
            movie_results = movie_results[0:5]
            tv_results = tv_results[0:5]
            
    movie_genre_dic, tv_genre_dic = genre_lists()

    show_id = []
    title = []
    overview = []
    poster = []
    date = []
    vote_avg = []
    vote_cnt = []
    genres = []
    show_type = []

    img_url = 'https://image.tmdb.org/t/p/w500'
    poster_none = 'https://cinemaone.net/images/movie_placeholder.png'

    for movie in movie_results:
        show_id.append(movie['id'])
        title.append(movie['title'])
        overview.append(movie['overview'].replace('\n', '\
        '))
        # overview.append(movie['overview'])
        if movie['poster_path'] == None or movie['poster_path'] == '':
            poster.append(poster_none)
        else:
            poster.append(img_url + movie['poster_path'])
        
        try:
            date.append(movie['release_date'][0:4])
        except:
            date.append('')
        
        try:
            vote_avg.append(round(float(movie['vote_average'])/2, 2))
        except: 
            vote_avg.append('')

        vote_cnt.append(movie['vote_count'])
        
        genre_str = ''
        for i in range(len(movie['genre_ids'])):
            try:
                genre_str += movie_genre_dic[int(movie['genre_ids'][i])]
                if i < len(movie['genre_ids']) - 1:
                    genre_str += ', '
            except:
                continue
        genres.append(genre_str)

        show_type.append('movie')

    for movie in tv_results:
        show_id.append(movie['id'])
        title.append(movie['name'])
        overview.append(movie['overview'].replace('\n', '\
        '))
        # overview.append(movie['overview'])
        if movie['poster_path'] == None or movie['poster_path'] == '':
            poster.append(poster_none)
        else:
            poster.append(img_url + movie['poster_path'])
        
        try:
            date.append(movie['first_air_date'][0:4])
        except:
            date.append('')
        
        try:
            vote_avg.append(round(float(movie['vote_average'])/2, 2))
        except: 
            vote_avg.append('')

        vote_cnt.append(movie['vote_count'])

        genre_str = ''
        for i in range(len(movie['genre_ids'])):
            try:
                genre_str += movie_genre_dic[int(movie['genre_ids'][i])]
                if i < len(movie['genre_ids']) - 1:
                    genre_str += ', '
            except:
                continue
        genres.append(genre_str)

        show_type.append('tv')

    data = basic_info()
    return render_template('home.html', trending_titles=data[0], trending_backdrops=data[1], dates=data[2], tv_titles=data[3], tv_backdrops=data[4], air_dates=data[5], search_ids=show_id, search_titles=title, search_overviews=overview, search_posters=poster, search_dates=date, search_avgs=vote_avg, search_cnts=vote_cnt, search_genres=genres, search='true', search_types=show_type)
    # return Response(200)

def search_movie(keyword):
    movie_url = 'https://api.themoviedb.org/3/search/movie'
    api_key = '?api_key=9152d19da914b763bbea03feeaebd8b0'
    end_url = '&language=en-US&page=1&include_adult=false'
    r = requests.get(movie_url + api_key + '&query=' + keyword + end_url)
    return r.json()['results']

def search_tv(keyword):
    tv_url = 'https://api.themoviedb.org/3/search/tv'
    api_key = '?api_key=9152d19da914b763bbea03feeaebd8b0'
    end_url = '&language=en-US&page=1&include_adult=false'
    r = requests.get(tv_url + api_key + '&query=' + keyword + end_url)
    return r.json()['results']

def genre_lists():
    movie_genre_url = 'https://api.themoviedb.org/3/genre/movie/list?api_key=9152d19da914b763bbea03feeaebd8b0&language=en-US'
    movie_genre_r = requests.get(movie_genre_url)
    movie_genres = movie_genre_r.json()['genres']
    
    # app.logger.debug(movie_genres)
    
    movie_genre_dic = {0: 'default'}
    for genre in movie_genres:
        genre_id = int(genre['id'])
        movie_genre_dic[genre_id] = genre['name']

    tv_genre_url = 'https://api.themoviedb.org/3/genre/tv/list?api_key=9152d19da914b763bbea03feeaebd8b0&language=en-US'
    tv_genre_r = requests.get(tv_genre_url)
    tv_genres = tv_genre_r.json()['genres']
    tv_genre_dic = {0: 'default'}
    for genre in tv_genres:
        genre_id = int(genre['id'])
        tv_genre_dic[genre_id] = genre['name']
    
    return movie_genre_dic, tv_genre_dic
@app.route('/info', methods=['POST'])
def info():
    show_id = request.args.get('show_id')
    show_type = request.args.get('show_type')

    movie_info_url = 'https://api.themoviedb.org/3/movie/'
    tv_info_url = 'https://api.themoviedb.org/3/tv/'
    ending = '?api_key=9152d19da914b763bbea03feeaebd8b0&language=en-US'
    img_url = 'https://image.tmdb.org/t/p/w500'

    if show_type == 'movie':
        info_r = requests.get(movie_info_url + show_id + ending)
        info = info_r.json()
        show_id = str(info['id'])
        title = info['title']
        runtime = info['runtime']
        date = info['release_date']
        overview = info['overview']

        languages = info['spoken_languages']
        language_str = ''
        for i in range(len(languages)):
            language_str += languages[i]['name']
            if i < len(languages) - 2:
                language_str += ', '
        
        vote_avg = str(round(float(info['vote_average'])/2, 2))
        vote_cnt = info['vote_count']

        if info['poster_path'] == None or info['poster_path'] == '':
            poster = 'https://cinemaone.net/images/movie_placeholder.png'
        else:
            poster = img_url + info['poster_path']

        if info['backdrop_path'] == None or info['backdrop_path'] == '':
            backdrop = 'https://bytes.usc.edu/cs571/s21_JSwasm00/hw/HW6/imgs/movie-placeholder.jpg'
        else:
            backdrop = img_url + info['backdrop_path']

        genre_list = info['genres']
        genre_str = ''
        for i in range(len(genre_list)):
            genre_str += genre_list[i]['name']
            if i < len(genre_list) - 1:
                genre_str += ', '

        credit_r = requests.get(movie_info_url + show_id + '/credits' + ending)
        credit = credit_r.json()['cast']
        actors = []
        for i in range(8): 
            try:
                actor = {}
                actor['char'] = credit[i]['character']
                actor['name'] = credit[i]['name']
                if credit[i]['profile_path'] == None or credit[i]['profile_path'] == '':
                    actor['profile'] = 'https://bytes.usc.edu/cs571/s21_JSwasm00/hw/HW6/imgs/person-placeholder.png'
                else:
                    actor['profile'] = str(img_url) + credit[i]['profile_path']
                actors.append(actor)
            except:
                # app.logger.debug('actor count: ' + str(i))
                break

        review_r = requests.get(movie_info_url + show_id + '/reviews' + ending)
        review = review_r.json()['results']
        comments = []
        # app.logger.debug(review)
        for i in range(5): 
            try:
                comment = {}
                comment['username'] = review[i]['author_details']['username']
                comment['content'] = review[i]['content']
                comment['rating'] = review[i]['author_details']['rating']

                created_at = review[i]['created_at']
                created = created_at.split('-')
                comment['created_at'] = created[0] + '/' + created[1] + '/' + created[2][0:2]

                comments.append(comment)
            except:
                break

        returning_obj = {
            'id': show_id,
            'title': title,
            'runtime': runtime,
            'date': date,
            'overview': overview,
            'language': language_str,
            'vote_avg': vote_avg,
            'vote_cnt': vote_cnt,
            'poster': poster,
            'backdrop': backdrop,
            'genre': genre_str,
            'credits': actors,
            'reviews': comments
        }
        return jsonify(returning_obj)
    else:
        info_r = requests.get(tv_info_url + show_id + ending)
        info = info_r.json()
        show_id = str(info['id'])
        title = info['name']
        runtime = info['episode_run_time']
        date = info['first_air_date']
        num_seasons = info['number_of_seasons']
        overview = info['overview']

        languages = info['spoken_languages']
        language_str = ''
        for i in range(len(languages)):
            language_str += languages[i]['name']
            if i < len(languages) - 2:
                language_str += ', '
        
        vote_avg = str(round(float(info['vote_average'])/2, 2))
        vote_cnt = info['vote_count']

        if info['poster_path'] == None or info['poster_path'] == '':
            poster = 'https://cinemaone.net/images/movie_placeholder.png'
        else:
            poster = img_url + info['poster_path']

        if info['backdrop_path'] == None or info['backdrop_path'] == '':
            backdrop = 'https://bytes.usc.edu/cs571/s21_JSwasm00/hw/HW6/imgs/movie-placeholder.jpg'
        else:
            backdrop = img_url + info['backdrop_path']

        genre_list = info['genres']
        genre_str = ''
        for i in range(len(genre_list)):
            genre_str += genre_list[i]['name']
            if i < len(genre_list) - 1:
                genre_str += ', '

        credit_r = requests.get(tv_info_url + show_id + '/credits' + ending)
        credit = credit_r.json()['cast']
        actors = []
        # app.logger.debug('act: ' + str(credit))
        for i in range(8): 
            # app.logger.debug('actor: ' + str(credit[i-1]))
            try:
                actor = {}
                actor['char'] = credit[i]['character']
                actor['name'] = credit[i]['name']
                if credit[i]['profile_path'] == None or credit[i]['profile_path'] == '':
                    actor['profile'] = 'https://bytes.usc.edu/cs571/s21_JSwasm00/hw/HW6/imgs/person-placeholder.png'
                else:
                    actor['profile'] = str(img_url) + credit[i]['profile_path']
                actors.append(actor)
            except:
                # app.logger.debug('except')
                break

        review_r = requests.get(tv_info_url + show_id + '/reviews' + ending + '&page=1')
        review = review_r.json()
        comments = []
        
        for i in range(5): 
            try:
                comment = {}
                comment['username'] = review[i]['author_details']['username']
                comment['content'] = review[i]['content']
                comment['rating'] = review[i]['author_details']['rating']
                
                created_at = review[i]['created_at']
                created = created_at.split('-')
                comment['created_at'] = created[0] + '/' + created[1] + '/' + created[2][0:2]
                
                comments.append(comment)
            except:
                break

        returning_obj = {
            'id': show_id,
            'title': title,
            'runtime': runtime,
            'date': date,
            'num_seasons': num_seasons,
            'overview': overview,
            'language': language_str,
            'vote_avg': vote_avg,
            'vote_cnt': vote_cnt,
            'poster': poster,
            'backdrop': backdrop,
            'genre': genre_str,
            'credits': actors,
            'reviews': comments
        }
        return jsonify(returning_obj)
