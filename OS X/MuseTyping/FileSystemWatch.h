//
//  FileSystemWatch.h
//  MuseTyping
//
//  Created by Aldrin Balisi on 2014-10-04.
//
//

#import <Foundation/Foundation.h>

@interface FileSystemWatch : NSObject

- (void)watchFileAtPath:(NSString*)path target:(id)target action:(SEL)action;
- (void)stopWatching;

@end

