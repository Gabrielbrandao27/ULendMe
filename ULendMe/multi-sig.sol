// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MultiSigNFTWallet is Ownable {
    address public owner1;
    address public owner2;
    address public currentHolder;
    mapping(address => mapping(uint256 => bool)) public approvals;
    IERC721 public nftContract;

    event NFTDeposited(address indexed from, uint256 tokenId);
    event NFTWithdrawn(address indexed to, uint256 tokenId);

    modifier onlyOwners() {
        require(msg.sender == owner1 || msg.sender == owner2, "Not an owner");
        _;
    }

    modifier bothApproved(uint256 tokenId) {
        require(approvals[owner1][tokenId] && approvals[owner2][tokenId], "Both owners must approve");
        _;
    }

    constructor(address _owner1, address _owner2, address _nftContract) Ownable(_owner1) {
        owner1 = _owner1;
        owner2 = _owner2;
        nftContract = IERC721(_nftContract);
    }

    function depositNFT(uint256 tokenId) external onlyOwners {
        require(nftContract.ownerOf(tokenId) == msg.sender, "Not the owner of the NFT");
        nftContract.transferFrom(msg.sender, address(this), tokenId);
        approvals[owner1][tokenId] = false;
        approvals[owner2][tokenId] = false;
        currentHolder = address(this);
        emit NFTDeposited(msg.sender, tokenId);
    }

    function approveTransfer(uint256 tokenId) external onlyOwners {
        approvals[msg.sender][tokenId] = true;
    }

    function transferNFT(address to, uint256 tokenId) external onlyOwners bothApproved(tokenId) {
        require(currentHolder == address(this), "NFT is not held by the contract");
        nftContract.transferFrom(address(this), to, tokenId);
        approvals[owner1][tokenId] = false;
        approvals[owner2][tokenId] = false;
        currentHolder = to;
        emit NFTWithdrawn(to, tokenId);
    }

    function returnNFT(uint256 tokenId) external onlyOwners {
        require(currentHolder != address(this), "NFT is already held by the contract");
        nftContract.transferFrom(currentHolder, owner1, tokenId);
        approvals[owner1][tokenId] = false;
        approvals[owner2][tokenId] = false;
        currentHolder = address(this);
        emit NFTWithdrawn(owner1, tokenId);
    }
}

