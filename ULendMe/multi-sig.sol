pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

contract NFTLending {
    address public dAppAddress;
    address public borrower;
    uint public lendingEndTime;
    IERC721 public nftContract;
    uint public tokenId;
    bool public lendingActive;
    
    modifier onlyDApp() {
        require(msg.sender == dAppAddress, "Caller is not the dApp");
        _;
    }
    
    modifier onlyBorrower() {
        require(msg.sender == borrower, "Caller is not the borrower");
        _;
    }
    
    modifier lendingNotActive() {
        require(!lendingActive, "Lending is already active");
        _;
    }
    
    modifier lendingActiveOnly() {
        require(lendingActive, "Lending is not active");
        _;
    }
    
    constructor(address _dAppAddress, address _nftContract, uint _tokenId, uint _lendingDuration) {
        dAppAddress = _dAppAddress;
        nftContract = IERC721(_nftContract);
        tokenId = _tokenId;
        lendingEndTime = block.timestamp + _lendingDuration;
    }
    
    function lendNFT(address _borrower) external onlyDApp lendingNotActive {
        borrower = _borrower;
        lendingActive = true;
        nftContract.transferFrom(dAppAddress, address(this), tokenId);
    }
    
    function returnNFT() external onlyDApp lendingActiveOnly {
        nftContract.transferFrom(address(this), dAppAddress, tokenId);
        lendingActive = false;
    }
    
    function getNFT() external view returns (address, uint) {
        return (address(nftContract), tokenId);
    }
    
    function isLendingActive() external view returns (bool) {
        return lendingActive;
    }
    
    function extendLending(uint _additionalDuration) external onlyDApp lendingActiveOnly {
        lendingEndTime += _additionalDuration;
    }
    
    function terminateLending() external onlyDApp lendingActiveOnly {
        lendingActive = false;
        nftContract.transferFrom(address(this), dAppAddress, tokenId);
    }
}