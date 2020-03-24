# utils

Utilities, obviously.

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

---  
## License

Copyright (C) 2016-2020 Ronald E. Robertson <ronaldrobertson42@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
