# wskenv
a CLI-based tool for managing multiple `.wskprops` of wsk command

- Get help
  ```
  $ wskenv.py -h
  usage: wskenv.py [-h] {create,remove,activate,list,show,cd} ...

  a CLI-based tool for managing multiple `.wskprops` of wsk command

  optional arguments:
    -h, --help            show this help message and exit

  available commands:
    {create,remove,activate,list,show,cd}
      create              create an wsk-environment
      remove              remove an wsk-environment
      activate            activate an wsk-environment
      list                list all the wsk-environment's
      show                show current wsk environment properties
      cd                  when you wish to get into wskenvs directory
  ```

- List all wsk environments created so far
  ``` 
  $ wskenv.py list
  [ERR] It is empty
  ```

- Create wsk environments
  ```
  $ wskenv.py create -h
  usage: wskenv.py create [-h] wskenv api_host auth

  positional arguments:
    wskenv      alias for the environment
    api_host    url or ip address
    auth        in form of `uuid:key`

  optional arguments:
    -h, --help  show this help message and exit
  ```
  ```
  $ wskenv.py create frisb-guest https://frisb.kakao.com df250ac1-d32e-4172-8566-5743b16ecfda:akXi2WpnTlWv47LiG4VAaH14A22AF7T3MiDeOfrzaqDKGFDh7v8R4NxIMVq4wzbC
  [OK] frisb-guest is created
  [OK] frisb-guest is activated
  ```
  ```
  $ wskenv.py create local-guest 192.168.33.16 03c4ef38-3a25-4595-ab98-0c3060f5b329:4VO7AkkUNtBDdJCUL8VCbiuzdA5UukCLCfgLL4fiT8J3eII1HeBIzs3vDAAm5UDr
  [OK] local-guest is created
  [OK] local-guest is activated
  ```

- List all wsk environments
  ```
  $ wskenv.py list
    frisb-guest
  * local-guest
  ```

- Check out currently active wsk environment in detail
  ```
  $ wskenv.py show
    [NAME] frisb-guest
    [HOST] 192.168.33.16
    [AUTH] 03c4ef38-3a25-4595-ab98-0c3060f5b329:4VO7AkkUNtBDdJCUL8VCbiuzdA5UukCLCfgLL4fiT8J3eII1HeBIzs3vDAAm5UDr
  ```

- Activate another wsk environment
  ```
  $ wskenv.py activate frisb-guest
  [OK] frisb-guest is activated
  ```

- Whenever not sure on what environment you are
  ```
  $ wskenv.py show
    [NAME] frisb-guest
    [HOST] https://frisb.kakao.com
    [AUTH] df250ac1-d32e-4172-8566-5743b16ecfda:akXi2WpnTlWv47LiG4VAaH14A22AF7T3MiDeOfrzaqDKGFDh7v8R4NxIMVq4wzbC
  ```
