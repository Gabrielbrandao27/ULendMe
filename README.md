# ULendMe

Made by: Gabriel and Marcelo

> This is a work in progress.

## About the dApp

Because NFTs are completely unique, if someone wants to make use of one (be it for gaming, for access or any needs you may have),<br>
they would have to buy it, and the person that had access to it will loose it, and won't be able to access it anymore.<br><br>

This dApp enables users to utilize NFTs without having to pay it's full price and without having to worry about possession changing.<br>
At the same time, lenders can make a profit of their NFTs without losing them, not having to worry about selling and loosing it's possession.<br>
<br>
This dApp will provide a plataform for:
- Creating Offers for the NFTs avaiable in your wallet (we will use Metamask)
- Browsing a Catalog with all the NFTs avaiable to borrow
- Choosing the NFT you want and borrowing it
- Seeing the offers you've made and their status
<br><br>
Now we will go through how to build, run and interact with the dApp. As mentioned above, this is a work in progress, and not all features are avaiable. Currently, it's only possible to create NFT offers.

### Building and Running the dApp

To run Back-end:

```shell
- cd ULendMe/
- sunodo build
- sunodo run
```

To run Front-end Console:

```shell
- cd sunodo-frontend-console/
- yarn && yarn build
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

### Handling ERC721 Tokens (WORK IN PROGRESS!)

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


- Checking your wallet balance (Work in progress!):<br>
balance/ether/{wallet}/{token_addres}/{token_id}

```shell
yarn start inspect --payload "balance/erc721/0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266/0xae7f61eCf06C65405560166b259C54031428A9C4/0"
```