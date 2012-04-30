package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentTransfer;
	import Elixys.Views.SequenceRun;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObjectContainer;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.geom.Point;

	// This transfer subview is an extension of the subview unit operation base class
	public class SubviewTransfer extends SubviewUnitOperationBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewTransfer(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, nButtonWidth, ComponentTransfer.COMPONENTTYPE, RUN_TRANSFER, attributes);

			// Initialize run mode
			if (m_sMode == Constants.RUN)
			{
				// Get references to the view components
				m_pVideoIconContainer1 = Form(findViewById("videobase_iconcontainer1"));
				m_pVideoLabel1 = UILabel(findViewById("videobase_label1"));
				m_pVideoLabelContainer1 = Form(findViewById("videobase_labelcontainer1"));
				m_pVideoIconContainer2 = Form(findViewById("videobase_iconcontainer2"));
				m_pVideoLabel2 = UILabel(findViewById("videobase_label2"));
				m_pVideoLabelContainer2 = Form(findViewById("videobase_labelcontainer2"));
				m_pVideoContainerParent = Form(findViewById("videobase_videocontainerparent"));
				
				// Add the video icons
				m_pVideoIconSkin1 = AddSkinAt(videoIcon_mc, 0);
				m_pVideoIconSkin2 = AddSkinAt(videoIcon_mc, 0);

				// Create the video containers
				m_pVideoContainerSingle = new Form(m_pVideoContainerParent, RUN_VIDEOCONTAINER1, m_pVideoContainerParent.attributes);
				m_pVideoContainerDual1 = new Form(m_pVideoContainerParent, RUN_VIDEOCONTAINER2, m_pVideoContainerParent.attributes);
				m_pVideoContainerDual2 = new Form(m_pVideoContainerParent, RUN_VIDEOCONTAINER3, m_pVideoContainerParent.attributes);

				// Find the parent sequence run
				var pParent:DisplayObjectContainer = screen;
				while ((pParent != null) && !(pParent is SequenceRun))
				{
					pParent = pParent.parent;
				}
				if (pParent is SequenceRun)
				{
					m_pSequenceRun = pParent as SequenceRun;
				}
				
				// Initialize the layout
				AdjustPositions();
			}
		}
		
		/***
		 * Member functions
		 **/
		
		// Updates the subview
		protected override function Update():void
		{
			// Update run mode
			if (m_sMode == Constants.RUN)
			{
				if (m_pComponent)
				{
					var pComponent:ComponentTransfer = m_pComponent as ComponentTransfer;
					if (pComponent.Mode == "Trap")
					{
						// Set the video labels
						m_pVideoLabel1.text = "REACTOR " + pComponent.SourceReactor;
						m_pVideoLabel1.visible = false;
						m_pVideoIconSkin2.visible = false;
						
						// Update the video stream if we're running and visible
						if (m_pRunState.Running && visible)
						{
							//m_pSequenceRun.HideVideo(m_pVideoContainerDual1);
							//m_pSequenceRun.HideVideo(m_pVideoContainerDual2);
							//m_pSequenceRun.SetVideo(pComponent.SourceReactor, m_pVideoContainerSingle);
						}
					}
					else
					{
						// Set the video labels
						m_pVideoLabel1.text = "REACTOR " + pComponent.SourceReactor;
						m_pVideoLabel1.visible = true;
						m_pVideoLabel2.text = "REACTOR " + pComponent.TargetReactor;
						m_pVideoIconSkin2.visible = true;
						
						// Update the video stream if we're running and visible
						if (m_pRunState.Running && visible)
						{
							//m_pSequenceRun.HideVideo(m_pVideoContainerSingle);
							//m_pSequenceRun.SetVideo(pComponent.SourceReactor, m_pVideoContainerDual1);
							//m_pSequenceRun.SetVideo(pComponent.TargetReactor, m_pVideoContainerDual2);
						}
					}
				}
			}
			
			// Call the base implementation
			super.Update();
		}
		
		// Adjusts the view component positions
		protected override function AdjustPositions():void
		{
			// Handle based on our mode
			if (m_sMode == Constants.RUN)
			{
				// Ignore if we haven't finished construction
				if (m_pVideoIconContainer1 == null)
				{
					return;
				}
				
				// Call the base implementation
				super.AdjustPositions();
				
				// Adjust the video icon positions
				var pUpperLeft:Point = globalToLocal(m_pVideoIconContainer1.localToGlobal(new Point(0, 0)));
				m_pVideoIconSkin1.x = pUpperLeft.x;
				m_pVideoIconSkin1.y = pUpperLeft.y + ((m_pVideoIconContainer1.attributes.height - m_pVideoIconSkin1.height) / 2);
				pUpperLeft = globalToLocal(m_pVideoIconContainer2.localToGlobal(new Point(0, 0)));
				m_pVideoIconSkin2.x = pUpperLeft.x;
				m_pVideoIconSkin2.y = pUpperLeft.y + ((m_pVideoIconContainer2.attributes.height - m_pVideoIconSkin2.height) / 2);
				
				// Adjust the video label positions
				m_pVideoLabel1.x = 0;
				m_pVideoLabel1.y = (m_pVideoLabelContainer1.attributes.height - m_pVideoLabel1.textHeight) / 2;
				m_pVideoLabel2.x = 0;
				m_pVideoLabel2.y = (m_pVideoLabelContainer2.attributes.height - m_pVideoLabel2.textHeight) / 2;

				// Adjust the video container positions
				m_pVideoContainerSingle.x = m_pVideoContainerParent.attributes.width * SINGLE_LEFTGAP / 100;
				m_pVideoContainerSingle.width = (m_pVideoContainerParent.attributes.width * SINGLE_VIDEO / 100);
				m_pVideoContainerDual1.x = m_pVideoContainerParent.attributes.width * DOUBLE_LEFTGAP / 100;
				m_pVideoContainerDual1.width = (m_pVideoContainerParent.attributes.width * DOUBLE_LEFTVIDEO / 100);
				m_pVideoContainerDual2.x = m_pVideoContainerParent.attributes.width * (DOUBLE_LEFTGAP + DOUBLE_LEFTVIDEO + DOUBLE_CENTERGAP) / 100;
				m_pVideoContainerDual2.width = (m_pVideoContainerParent.attributes.width * DOUBLE_RIGHTVIDEO / 100);
				m_pVideoContainerSingle.y = m_pVideoContainerDual1.y = m_pVideoContainerDual2.y = 0;
				m_pVideoContainerSingle.height = m_pVideoContainerDual1.height = m_pVideoContainerDual2.height = m_pVideoContainerParent.attributes.height;
				trace("Single (" + m_pVideoContainerSingle.x + ", " + m_pVideoContainerSingle.y + ") x (" + m_pVideoContainerSingle.scaleX + ", " +
					m_pVideoContainerSingle.scaleY + "), (" + (m_pVideoContainerSingle.x * m_pVideoContainerSingle.scaleX) + ", " +
					(m_pVideoContainerSingle.y * m_pVideoContainerSingle.scaleY) + ")");
				trace("Dual 1 (" + m_pVideoContainerDual1.x + ", " + m_pVideoContainerDual1.y + ") x (" + m_pVideoContainerDual1.scaleX + ", " +
					m_pVideoContainerDual1.scaleY + "), (" + (m_pVideoContainerDual1.x * m_pVideoContainerDual1.scaleX) + ", " +
					(m_pVideoContainerDual1.y * m_pVideoContainerDual1.scaleY) + ")");
				trace("Dual 2 (" + m_pVideoContainerDual2.x + ", " + m_pVideoContainerDual2.y + ") x (" + m_pVideoContainerDual2.scaleX + ", " +
					m_pVideoContainerDual2.scaleY + "), (" + (m_pVideoContainerDual2.x * m_pVideoContainerDual2.scaleX) + ", " +
					(m_pVideoContainerDual2.y * m_pVideoContainerDual2.scaleY) + ")");
			}
			else
			{
				// Call the base implementation
				super.AdjustPositions();
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Run XML
		protected static const RUN_TRANSFER:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows id="unitoperationcontainer" heights="3%,6%,5%,75%,11%" gapV="0">
					<frame />
					<columns widths="19,7%,5,43%,7%,5,43%" gapH="0">
						<frame />
						<frame id="videobase_iconcontainer1" />
						<frame />
						<frame id="videobase_labelcontainer1">
							<label id="videobase_label1" useEmbedded="true">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
							</label>
						</frame>
						<frame id="videobase_iconcontainer2" />
						<frame />
						<frame id="videobase_labelcontainer2">
							<label id="videobase_label2" useEmbedded="true">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
							</label>
						</frame>
					</columns>
					<frame />
					<frame id="videobase_videocontainerparent" />
					<frame />
				</rows>
			</frame>;
		protected static const RUN_VIDEOCONTAINER:XML = 
			<frame alignH="fill" alignV="fill" />;
		protected static const RUN_VIDEOCONTAINER1:XML = 
			<frame alignH="fill" alignV="fill" background="#FF0000" />;
		protected static const RUN_VIDEOCONTAINER2:XML = 
			<frame alignH="fill" alignV="fill" background="#00FF00" />;
		protected static const RUN_VIDEOCONTAINER3:XML = 
			<frame alignH="fill" alignV="fill" background="#0000FF" />;
		
		// View components
		protected var m_pVideoIconContainer1:Form;
		protected var m_pVideoLabel1:UILabel;
		protected var m_pVideoLabelContainer1:Form;
		protected var m_pVideoIconSkin1:MovieClip;
		protected var m_pVideoIconContainer2:Form;
		protected var m_pVideoLabel2:UILabel;
		protected var m_pVideoLabelContainer2:Form;
		protected var m_pVideoIconSkin2:MovieClip;
		protected var m_pVideoContainerParent:Form;
		protected var m_pVideoContainerSingle:Form;
		protected var m_pVideoContainerDual1:Form;
		protected var m_pVideoContainerDual2:Form;
		
		// Parent sequence run
		protected var m_pSequenceRun:SequenceRun;

		// Layout constants
		protected var SINGLE_LEFTGAP:uint = 19;
		protected var SINGLE_VIDEO:uint = 67;
		protected var SINGLE_RIGHTGAP:uint = 14;
		protected var DOUBLE_LEFTGAP:uint = 5;
		protected var DOUBLE_LEFTVIDEO:uint = 40;
		protected var DOUBLE_CENTERGAP:uint = 5;
		protected var DOUBLE_RIGHTVIDEO:uint = 40;
		protected var DOUBLE_RIGHTGAP:uint = 0;
	}
}
