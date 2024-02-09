// SPDX-License-Identifier: MIT

pragma solidity ^0.8;

contract test {
    // bytes32 indexed keyHash,
    // uint256 requestId,
    // uint256 preSeed,
    // uint64 indexed subId,
    // uint16 minimumRequestConfirmations,
    // uint32 callbackGasLimit,
    // uint32 numWords,
    event Event1(
        uint32 numWords,
        address indexed sender
    );
    // bytes32 keyHash = address(0);
    bytes32 keyHash;
    // uint256 requestId = 1;
    // uint256 preSeed = 1;
    // uint64 subId = 1;
    // uint16 minimumRequestConfirmations = 3;
    // uint32 callbackGasLimit = 13000;
    uint32 numWords = 1;
    address sender = address(0);
    
    function a() public view returns (uint256) {
        return tx.gasprice;
    }

    function aa() public returns (uint256){
        numWords = 2;
        return tx.gasprice;
    }
    
    function b() public view returns (uint256, uint256) {
        return (block.number, block.prevrandao);
    }

    function c(bytes32 t) public{
    // function c() public{
        keyHash = t;
        emit Event1(numWords, sender);
    }

}
