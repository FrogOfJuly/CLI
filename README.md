```shell
clone https://github.com/FrogOfJuly/CLI
cd CLI
```
Архитектура:
```
IO-loop   ->   lark parser
   ^                |
   |                v
 execute  <-   cmd/stmt oblect                 
```


* Запустить CLI:
    ```shell
    make run
    ```

* Запустить тесты:
    ```shell
    make run
    ```

* Запустить flake8:
    ```shell
    make run_flake8
    ```
* Запустить pylint:
    ```shell
    make run_pylint
    ```
* Запустить mypy:
    ```shell
    make run_mypy
    ```