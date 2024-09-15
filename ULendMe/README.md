> First run this:
- In one terminal: sunodo run --no-backend --epoch-duration=10

- Another terminal: ROLLUP_HTTP_SERVER_URL=http://localhost:8080/host-runner python3 dapp.py

- Compile and Deploy the Smart Contracts on Remix

- Another terminal: sunodo send -> dapp address

- Another terminal: yarn && yarn build

>>>>>
> Tutorial on Minting NFTs through the dApp:
- yarn start input send --payload '{"method": "erc721_mint"}' --address 0xab7528bb862fb57e8a2bcd567a2e929a0be56a5e
- yarn start voucher list
- yarn start voucher execute --index 0 --input 1 --address 0xab7528bb862fb57e8a2bcd567a2e929a0be56a5e

- Import token on metamask
- Approve token use through portal erc721 on remix
- sunodo send-> erc721 deposit


>>>>>
> Tutorial on Lising NFTs on the Catalog through the dApp:

- Sending input for posting NFT
```shell
yarn start input send --payload '{
    "method": "post_nft_for_lending",
    "token_id": 1,
    "price": 100,
    "lending_period": 7
}' --address 0xab7528bb862fb57e8a2bcd567a2e929a0be56a5e
```

- Inspecting Catalog
```shell
yarn start inspect --payload "Catalog"
```

>>>>>
> Tutorial on Marking for Borrowing an NFT on the Catalog through the dApp:

- Sending input for choosing NFT for Borrowing
```shell
yarn start input send --payload '{
    "method": "borrow_nft",
    "owner": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "token_id": 1
}' --address 0xab7528bb862fb57e8a2bcd567a2e929a0be56a5e --accountIndex '1'
```