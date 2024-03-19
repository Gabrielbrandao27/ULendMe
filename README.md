# ULendMe

Made by: Gabriel and Marcelo


### Running dApp

To run Back-end:

```shell
- cd ULendMe/
- sunodo build
- sunodo run
```

To run Front-end Console:

```shell
- cd sunodo-frontend-console/
- yarn
- yarn build
```

### Sending Inputs

The `input send` command adds inputs to a Cartesi Rollups DApp and has the following format:

```shell
yarn start input send --payload [message] <options>
```

[message] will be: post_type, wallet, nft_id, post_timestamp, loan_period

So, for example:
```shell
yarn start input send --payload "offer,0x1234,macaco#123,0.0065,18-03-2024-19:30,7"
```


### Inspecting Inputs

The `yarn start inspect --payload ''` can inspect the posts of the dApp

```shell
yarn start inspect --payload '<payload-here>'
```

So, for example:
```shell
yarn start inspect --payload "posts"
```