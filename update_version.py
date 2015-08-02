'''
Created on Jul 10, 2015

@author: sgee
'''
import io, sys, getopt
# import src.silo.__version__.py

def main(argv):
    
    version_file = open('src/silo/__version__.py', 'r')
    tmp_version = version_file.read()
    version_file.close()
    print tmp_version
    keys = tmp_version.split("\"")
    version = keys[1]
    
    print 'Current Version: ', version
    
    keys = version.split('.')
    major_version = int(keys[0])
    secondary_version = int(keys[1])
    tertiary_version = int(keys[2])
    print 'major_version: ',major_version
    print 'secondary_version: ',secondary_version
    print 'tertiary_version: ',tertiary_version
#     for key in keys:
#         print key
               
    try:   
        options, args = getopt.getopt(argv, 'hmstr:', ['set'])
        for opt, arg in options:
            if opt in ('-m', '--major'):
                print 'Incrementing Major'
                major_version = major_version + 1
            elif opt in ('-s', '--secondary'):
                print 'Incrementing Secondary'
                secondary_version = secondary_version + 1
            elif opt in ('-t', '--tertiary'):
                print 'Incrementing Tertiary'
                tertiary_version = tertiary_version + 1
            elif opt in ('-r'):
                clr = list(arg)
                for rclr in clr:
                    print 'Reset: ', rclr
                    if rclr == 'm':
                        major_version = 0
                    elif rclr == 's':
                        secondary_version = 0
                    elif rclr == 't':
                        tertiary_version = 0
                    
                    
    except getopt.GetoptError:
        print 'update_version.py -m -s -t -r[mst]'
        print '\t-m Increment Master Version'
        print '\t-s Increment Secondary Version'
        print '\t-t Increment Tertiary Version'
        print '\t-rmst Reset [m] Master [s] Secondary [t] Tertiary Versions'
        sys.exit(2)
           
    #end for
    
    print 'major_version: ',major_version
    print 'secondary_version: ',secondary_version
    print 'tertiary_version: ',tertiary_version
    version = str(major_version) + '.' + str(secondary_version) + '.' + str(tertiary_version)
    version_file = open('src/silo/__version__.py', 'w')
    version_file.write('__version__=\"' + version + '\"')
    version_file.close()
#end main

if __name__ == '__main__':
    main(sys.argv[1:])
