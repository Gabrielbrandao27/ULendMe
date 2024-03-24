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

- The `input send` command adds inputs to a Cartesi Rollups DApp and has the following format:

```shell
yarn start input send --payload [message] <options>
```

[message] will be: nft_id, price, post_timestamp, loan_period

- So, for example:
```shell
yarn start input send --payload "offer,ape#123,0.0065,18-03-2024-19:30,7"
```

- Sending inputs using different accounts:
```shell
yarn start input send --payload 'offer,leopard#09,3.0,22-03-2024-20:30,30' --accountIndex '1'
```

### Handling ERC721 Tokens

- payload for transfering a ERC721 tokens:
```shell
yarn start input send --payload "
{
    "method": "erc721_transfer",
    "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "to": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
	"erc721": "0xae7f61eCf06C65405560166b259C54031428A9C4",
    "token_id": 0
}"
```

- payload for withdrawing a ERC721 token:
```shell
yarn start input send --payload "
{
    "method": "erc721_withdraw",
    "from": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
	"erc721": "0xae7f61eCf06C65405560166b259C54031428A9C4",
    "token_id": 1
}
```



### Inspecting Inputs

- The `yarn start inspect --payload ""` can inspect the posts of the dApp

```shell
yarn start inspect --payload '<payload-here>'
```

- So, for example:
```shell
yarn start inspect --payload "Catalog"
```
You will inspect all offers posted on the page


- And this command here:
```shell
yarn start inspect --payload "Status,0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
```
Allows you to check your private loaned tokens

- Checking your wallet balance:
balance/ether/{wallet}/{token_addres}/{token_id}

```shell
yarn start inspect --payload "balance/erc721/0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266/0xae7f61eCf06C65405560166b259C54031428A9C4/0"
```