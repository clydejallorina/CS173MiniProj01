# CS 173: Blockchain Development

## Mini Lab 01

Improve the provided lottery contract by adding the following features:

- Allow users to buy multiple tickets in the buy_ticket entrypoint in a single transaction. (Hint: pass number of tickets to buy in the parameters) 
- Add entrypoints that can be used by the admin to change ticket cost and maximum number of available tickets. (Hint: Only allow changing these parameters when no game is on i.e number of tickets sold is 0)

Additional features:

- Admins no longer need to provide a random number, source of randomness is now `sp.now`

> Contract can be found in Limanet with address: `KT1UHkKco748cEexfWqrxkQg4meCcQcQSNVv`
