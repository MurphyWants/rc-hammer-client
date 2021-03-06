class Variable_Holder:
    Command_Array = []
    Sleep_Time = 8
    """
    Sleep_Time in ms
    """

    """
    Set various status to be interperted by functions set_blinkstick and set_headlights
    """
    status_initial = False
    status_error = False
    status_connected = False


    last_pop = (0,0)

    def append_to_array(self, data):
        if isinstance(data[0], (int, float)) and isinstance(data[1], (int, float)):
            self.Command_Array.append((data[0], data[1]))

    def pop_array(self):
        data = "Null"
        try:
            data = self.Command_Array.pop(0)
            self.last_pop = data
            return data
        except IndexError:
            return (self.last_pop[0], 0)

    def get_status(self):
        return self.Status_Lights[self.Status_Current]

    def change_status(self, num):
        if isinstance(num, int):
            if (0 <= num) and (num <= (len(self.Status_Lights) +1)):
                self.Status_Current = num

    def get_headlights(self):
        return self.Headlight_Methods[self.Headlight_Current]

    def change_headlights(self, num):
        if isinstance(num, int):
            if (0 <= num) and (num <= (len(self.Headlight_Methods) +1)):
                self.Headlight_Current = num

    def get_sleep_time(self):
        return self.Sleep_Time

    def update_sleep_time(self, num):
        if isinstance(num, int):
            self.Sleep_Time = num
