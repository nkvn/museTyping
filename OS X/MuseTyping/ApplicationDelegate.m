#import "ApplicationDelegate.h"

@interface ApplicationDelegate ()
@property (nonatomic, strong) NSMutableArray *alphabet;
@property (nonatomic) NSUInteger letter;
@property (nonatomic) BOOL typing;
@property (nonatomic, strong) NSTimer *timer;
@end

@implementation ApplicationDelegate

@synthesize menubarController = _menubarController;

#pragma mark -

void *kContextActivePanel = &kContextActivePanel;

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    if (context == kContextActivePanel) {
    }
    else {
        [super observeValueForKeyPath:keyPath ofObject:object change:change context:context];
    }
}

#pragma mark - NSApplicationDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)notification
{
    // Install icon into the menu bar
    self.menubarController = [[MenubarController alloc] init];
    self.typing = NO;
    
    self.alphabet = [[NSMutableArray alloc] init];
    for (char a = 'a'; a <= 'z'; a++)
    {
        [self.alphabet addObject:[NSString stringWithFormat:@"%c", a]];
    }
    self.menubarController.statusItemView.action = @selector(togglePanel:);
    
#warning This file path is hard coded
    int fildes = open("/Users/kevin/Documents/wearables-hack/museTyping/jordanCode/test", O_RDONLY);
    
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_source_t source = dispatch_source_create(DISPATCH_SOURCE_TYPE_VNODE,fildes,
                                                      DISPATCH_VNODE_DELETE | DISPATCH_VNODE_WRITE | DISPATCH_VNODE_EXTEND | DISPATCH_VNODE_ATTRIB | DISPATCH_VNODE_LINK | DISPATCH_VNODE_RENAME | DISPATCH_VNODE_REVOKE,
                                                      queue);
    dispatch_source_set_event_handler(source, ^
    {
        if (_typing) {
            int pid = [[NSProcessInfo processInfo] processIdentifier];
            NSPipe *pipe = [NSPipe pipe];
            
            NSTask *task = [[NSTask alloc] init];
            task.launchPath = @"/usr/bin/automator";
#warning This file path is hard coded
            task.arguments = @[[NSString stringWithFormat:@"/Users/kevin/Documents/wearables-hack/museTyping/OS\ X/MuseTyping/Alphabet/%lu.workflow", (unsigned long)(self.letter - 2) % 26]];
            task.standardOutput = pipe;
            
            [task launch];
            NSLog(@"%lu, ",(unsigned long)self.letter);
        }
    });
    dispatch_source_set_cancel_handler(source, ^
    {
        //Handle the cancel
    });
    dispatch_resume(source);
}

- (NSApplicationTerminateReply)applicationShouldTerminate:(NSApplication *)sender
{
    // Explicitly remove the icon from the menu bar
    self.menubarController = nil;
    return NSTerminateNow;
}

#pragma mark - Actions

- (IBAction)togglePanel:(id)sender
{
    self.menubarController.hasActiveIcon = !self.menubarController.hasActiveIcon;
    self.typing = !self.typing;
    [self.menubarController.statusItem setTitle:nil];
    self.menubarController.statusItemView.image = self.typing ? nil : [NSImage imageNamed:@"Status"];
    self.menubarController.statusItemView.alternateImage = self.typing ? nil : [NSImage imageNamed:@"StatusHighlighted"];
    if (self.typing) {
        self.timer = [NSTimer scheduledTimerWithTimeInterval:0.5
                                                      target:self
                                                    selector:@selector(loopAlphabet)
                                                    userInfo:nil
                                                     repeats:YES];
    }
    else {
        [self.timer invalidate];
        self.timer = nil;
    }
}

- (void)loopAlphabet {
    self.menubarController.statusItemView.alternateImage = [NSImage imageNamed:[NSString stringWithFormat:@"%lu", (unsigned long)self.letter]];
    self.letter = (self.letter + 1) % 26;
}

#pragma mark - PanelControllerDelegate

- (StatusItemView *)statusItemViewForPanelController:(PanelController *)controller
{
    return self.menubarController.statusItemView;
}

@end
