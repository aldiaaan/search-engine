from src.domain import Domain
import multiprocessing 


def worker(domain):
  try:
    country = "UNKNOWN"
    try:      
      country = Domain.domain_name_for_country("http://" + domain.name)            
      name = domain.name
      print("[{}] {}".format(country, name))
      return country, domain.name
    except Exception:
      print("error using http://, trying with http for {}".format(domain.name))
      
    try:      
      country = Domain.domain_name_for_country("https://" + domain.name)            
      name = domain.name
      print("[{}] {}".format(country, name))
      return country, domain.name
    except Exception:
      print("error, skipping {}".format(domain.name))
    return country, domain.name
  except Exception as e:
    print("error on {}".format(domain.name))

def collect_stats(stats):
  
  stats = dict()

  for x in stats:
    print(x)
    if stats.get(x.country) != None:
      stats[x.country] += stats[x.country] + 1
    else: 
      stats[x.country] = 1
  
  return stats

def collect_domains():
  domains, total = Domain.find({
    "limit": 18446744073709551615,
    "start": 0,
    "query": "",
    "sort_total_pages": "DESC",
    "with_country": False
  })

  with multiprocessing.Pool() as pool: 
    results = pool.map(worker, domains) 
 
  print(results)
  print(collect_stats(results))
  