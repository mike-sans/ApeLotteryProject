// SPDX-License-Identifier: MIT

pragma solidity ^0.8;

contract test {
    function b() public view returns (uint256, uint256) {
        return (block.number, block.prevrandao);
    }

    function c(bytes32 _hash) public pure returns (bytes32) {
        return(_hash);
    }
}
