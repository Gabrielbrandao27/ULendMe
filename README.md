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

[message] will be: wallet, nft_id, price, post_timestamp, loan_period

So, for example:
```shell
yarn start input send --payload "0x1234,macaco#123,0.0065,18-03-2024-19:30,7"
```

Transfering NFTs can be done by using the following payload:
```shell
yarn start input send --payload ""
```




### Inspecting Inputs

The `yarn start inspect --payload ""` can inspect the posts of the dApp

```shell
yarn start inspect --payload '<payload-here>'
```

So, for example:
```shell
yarn start inspect --payload "Catalog"
```
You will inspect all offers posted on the page


And this command here:
```shell
yarn start inspect --payload "Status,0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266,0x1234"
```
Allows you to check your private loaned tokens
