## Usage

`python dataman.py KEYWORD DATABASE_IP`

Dataman use mongodb as its database. 
You should give the ip address of mongodb, 
and currently it uses the default port.

## Database Structure

Database is `cs579proj`.

Collections are `tweets` and `history`.

Collection `tweet` save the tweets got from Twitter.
The structure of `tweet` is:

``` text
{
    'keyword':      keyword,
    'created_at':   send time,
    'name':         name of sender,
    'user':         screen name of sender,
    'text':         the content of tweet
}
```

Collection `history` save the last saving `max_id`,
so next time when you start the searching you will
continue your progress and avoid the duplicated
results. The structure of `history` is:

``` text
{
    'keyword':  keyword,
    'time':     last search time,
    'max_id':   the max_id of last search
}
```