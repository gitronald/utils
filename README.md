# utils 0.1.8

Utilities, obviously. 

Here lie a bunch of utilities for general purpose and fairly specific tasks that I frequently come across while wrangling and analyzing data. I find it extremely useful to be able to quickly install this package via `pip install --upgrade git+https://github.com/gitronald/utils` and have these functions at my fingertips instead of rewriting them, or copy and pasting them into every project I work on.

Someday I might better document these functions, but let's be real, probably not. For people that aren't me, this is probably best used as a template from which you can create your own utils package. There are a ton of benefits to having a centralized repo for your utils, and I highly recommend it.  I tend to use the `utils`, `dtables`, and `timers` - which contain more general purpose functions, like writing json lines to a file - the most. The `logger` module also has a useful template for creating a custom logger for ongoing data collection tasks, which in my experience isn't that easy to come across. Other than that, who knows what's in here. Goodluck!

## dtables

## plot

## rankings

## stats

## timers

## web

## logger

Simplifying python logging to console and/or a file.

### Examples

Log to console only:  
```python
import logger
log = logger.Logger().start()
log.debug('new log who dis')
log.info('new log who dis')
log.warning('new log who dis')
try:
    print(potato)
except Exception as e:
    log.exception('a')
```

Log to file only:  
```python
import logger
log = logger.Logger('test.log', console=False).start()
log.debug('new log who dis')
log.info('new log who dis')
log.warning('new log who dis')
try:
    print(potato)
except Exception as e:
    log.exception('a')
```

Log to both:  
```python
import logger
log = logger.Logger('test.log').start()
log.debug('new log who dis')
log.info('new log who dis')
log.warning('new log who dis')
try:
    print(potato)
except Exception as e:
    log.exception('a')
```

Log detailed record to file:
```python
import logger
log = logger.Logger('test.log', file_format='detailed').start()
log.debug('new log who dis')
log.info('new log who dis')
log.warning('new log who dis')
try:
    print(potato)
except Exception as e:
    log.exception('a')
```

