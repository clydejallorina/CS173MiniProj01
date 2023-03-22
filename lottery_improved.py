import smartpy as sp

class Lottery(sp.Contract):
    def __init__(self):
        self.init(
            players = sp.map(l={}, tkey=sp.TNat, tvalue=sp.TAddress),
            ticket_cost = sp.tez(1),
            tickets_available = sp.nat(5),
            max_tickets = sp.nat(5),
            operator = sp.address("tz1fsmUpoggTWnL85PuS26Y9Ei5N21GwntDE"),
        )
    
    @sp.entry_point
    def buy_ticket(self, ticket_count):
        sp.set_type(ticket_count, sp.TNat)

        total_cost = sp.mul(ticket_count, self.data.ticket_cost)
        tickets_bought = sp.local("tickets_bought", 0)

        # Sanity checks
        sp.verify(ticket_count > 0, "TICKET COUNT NEEDS TO BE A POSITIVE INTEGER")
        sp.verify(self.data.tickets_available - ticket_count >= 0, "NO TICKETS AVAILABLE")
        sp.verify(sp.amount >= total_cost, "INVALID AMOUNT")

        # Storage updates
        ticket_counter = sp.as_nat(self.data.max_tickets - self.data.tickets_available)
        with sp.while_(tickets_bought.value < ticket_count):
            self.data.players[ticket_counter + tickets_bought.value] = sp.sender
            tickets_bought.value += 1
        self.data.tickets_available = sp.as_nat(self.data.tickets_available - ticket_count)

        # Return extra tez balance to the sender
        extra_balance = sp.amount - total_cost
        with sp.if_(extra_balance > sp.mutez(0)):
            sp.send(sp.sender, extra_balance)
            
    @sp.entry_point
    def change_lottery_params(self, ticket_cost, new_max_tickets):
        # ticket_cost : TNat : Cost in mutez
        # new_max_tickets : TNat : New max ticket count
        # Developer note: 1 tez = 1_000_000 mutez
        sp.set_type(ticket_cost, sp.TNat)
        sp.set_type(new_max_tickets, sp.TNat)
        
        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORIZED")
        sp.verify(self.data.max_tickets == self.data.tickets_available, "LOTTERY ALREADY RUNNING")
        
        self.data.max_tickets = new_max_tickets
        self.data.tickets_available = new_max_tickets
        self.data.ticket_cost = sp.utils.nat_to_mutez(ticket_cost)

    @sp.entry_point
    def end_game(self):
        random_number = sp.utils.seconds_of_timestamp(sp.now)

        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == 0, "GAME IS YET TO END")

        # Pick a winner
        winner_id = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_id]

        # Send the reward to the winner
        sp.send(winner_address, sp.balance)

        # Reset the game
        self.data.players = {}
        self.data.tickets_available = self.data.max_tickets

    @sp.entry_point
    def default(self):
        sp.failwith("NOT ALLOWED")

@sp.add_test(name = "main")
def test():
    scenario = sp.test_scenario()

    # Test accounts
    admin = sp.address("tz1fsmUpoggTWnL85PuS26Y9Ei5N21GwntDE")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    mike = sp.test_account("mike")
    charles = sp.test_account("charles")
    john = sp.test_account("john")

    # Contract instance
    lottery = Lottery()
    scenario += lottery

    # change lottery params
    scenario += lottery.change_lottery_params(ticket_cost=sp.nat(500000), new_max_tickets=sp.nat(10)).run(sender = admin)
    
    # buy_ticket
    scenario.h2("buy_ticket (valid test)")
    scenario += lottery.buy_ticket(1).run(amount = sp.tez(1), sender = alice)
    scenario += lottery.buy_ticket(2).run(amount = sp.tez(2), sender = bob)

    scenario.h2("buy_ticket (failure test)")
    scenario += lottery.buy_ticket(3).run(amount = sp.tez(1), sender = john, valid = False)
    scenario += lottery.buy_ticket(4).run(amount = sp.tez(1), sender = john, valid = False)

    scenario.h2("buy_ticket (close the lottery)")
    scenario += lottery.buy_ticket(4).run(amount = sp.tez(4), sender = charles)
    scenario += lottery.buy_ticket(3).run(amount = sp.tez(3), sender = alice)

    # end_game
    scenario.h2("end_game (valid test)")
    scenario += lottery.end_game().run(sender = admin)
