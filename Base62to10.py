baseChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

class BaseNConverter:      
    def baseNto10(self, number, base):
        #Input must be a string
        
        #Find the posistion of the number in the array.
        output = 0
        length = 0
        for x in number[::-1]:
            pos = baseChars.find(x)
            #It is an error if the value is > than the base.
            power = pow(base, length)
            output += power * pos
            
            length += 1
        return output
    
    def base10ToN(self, number, base):
        output = []
        
        quotient = 1;
        
        while quotient != 0:
            quotient, remainder = divmod(number, base)
            output.append(baseChars[remainder])
            number = quotient
            
        output.reverse()
        
        #TODO make sure that the conversion to a nu
        
        return ''.join(output)