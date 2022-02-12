import picar_4wd as fc

speed = 30

def main():
    while True:
        scan_list = fc.scan_step(35)
        if not scan_list:
            continue

        tmp = scan_list[3:7]
        print(tmp)
        if tmp != [2,2,2,2]:
            direction=random.randint(1,4):
            if direction == 1:
                fc.turn_right(speed)
            if direction == 2:
                fc.turn_right(speed)
            if direction == 3:
                fc.backward(speed)
        else:
            fc.forward(speed)

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()