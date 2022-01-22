from django.db import connection
from django.shortcuts import render


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def index(request):
    return render(request, 'index.html')


def query1():
    sql = """
    select *
    from Buying;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return dictfetchall(cursor)



















/* question 1*/
create view daily_investor_sector_count
as
    select b.tdate, b.id, count(distinct c.Sector) as sectors_daily_investor
from company c, buying b
where c.Symbol=b.Symbol
group by  b.tdate, b.id


create view diversed_investor
as
    select distinct d.id , I.name
from daily_investor_sector_count d, Investor I
where d.id=I.ID and sectors_daily_investor>=8


create view investors_buys
as
    select  d.name, s.Price*b.BQuantity as fullprice
from buying b, stock s, diversed_investor d
where b.tDate=s.tDate and b.id=d.id and b.Symbol=s.Symbol
group by d.name , s.Price*b.BQuantity


select name, round(sum(fullprice), 3) as Total_sum
from investors_buys
group by name
order by Total_sum desc




/* question 2*/

create view days_bought_per_company
as
select symbol, count(distinct tDate) as days_bought
from Buying
group by symbol



create view popular_companies
    as
    select symbol, days_bought
from days_bought_per_company
where days_bought>( select count(distinct tdate)
                        from Buying)/2



create view investor_stock_in_companies_count
    as
select symbol, id, sum(BQuantity) as stocks_in_company_for_investor
from Buying
group by id, symbol


create view top_investor_per_company
as
select symbol, max(stocks_in_company_for_investor) as max_investor
from investor_stock_in_companies_count
group by symbol

create view top_investor_per_company_withname
as
select t.symbol, i.Name, t.max_investor
from investor i, top_investor_per_company t, investor_stock_in_companies_count isic
where i.id=isic.id and t.symbol=isic.symbol and stocks_in_company_for_investor=max_investor and max_investor>10


select p.symbol, t.Name, t.max_investor
from popular_companies p, top_investor_per_company_withname t
where p.symbol=t.symbol
order by p.symbol

/*question 3*/

create view bought_once_companys
as
select Symbol , tDate
from buying
except
select b1.Symbol, b1.tDate
from buying b1, buying b2
where (b1.Symbol=b2.Symbol) and (b1.tDate!= b2.tDate or b1.ID!=b2.ID or b1.BQuantity!=b2.BQuantity)




CREATE view A as
select  s.Symbol, s.tDate ,s.Price
from Stock s, bought_once_companys b
where s.Symbol=b.Symbol and s.tDate>=b.tDate

CREATE VIEW B as
select Symbol, tDate ,Price
from A
except
select A.Symbol, A.tDate, A.Price from
A inner join bought_once_companys boc on A.Symbol = boc.Symbol and A.tDate = boc.tDate


create view c as
SELECT Symbol, MIN(tDate) as tDate
from B
GROUP BY Symbol


create view bought_once_companys_buying_date
as
select b.Symbol, b.tDate, s.Price
from bought_once_companys b , Stock s
where b.Symbol=s.Symbol and b.tDate=s.tDate



create view bought_once_companys_nextDate
as
select c.Symbol, c.tDate, s.Price
from c, Stock s
where c.Symbol=s.Symbol and c.tDate=s.tDate


create view groyse_mezia
as
select bd.Symbol, bd.tDate
from bought_once_companys_buying_date bd
where  ((((select bb.price
                 from bought_once_companys_nextDate bb
                  where bd.Symbol=bb.Symbol)-bd.Price)/bd.Price)*100 > 3)

select g.Symbol, g.tDate, i.Name
from groyse_mezia g,buying b, Investor i
where g.tDate=b.tDate and g.Symbol=b.Symbol and b.ID=i.ID

