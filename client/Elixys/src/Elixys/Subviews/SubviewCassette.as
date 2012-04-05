package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.utils.getQualifiedClassName;

	// This cassette subview is an extension of the subview base class
	public class SubviewCassette extends SubviewBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewCassette(screen:Sprite, sMode:String, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, ComponentCassette.COMPONENTTYPE, VIEW_CASSETTE, EDIT_CASSETTE, RUN_CASSETTE, 
				attributes);
		}

		/***
		 * Member functions
		 **/
		
		// Updates the component
		public override function UpdateComponent(pComponent:ComponentBase):void
		{
		}

		/***
		 * Member variables
		 **/

		// View cassette XML
		protected static const VIEW_CASSETTE:XML = 
			<columns gapH="0" widths="6%,88%,6%">
				<frame />
				<rows background={Styling.APPLICATION_BACKGROUND} gapV="0" heights="2%,8%,10,18%,72%">
					<frame />
					<label useEmbedded="true" alignH="left" alignV="centre">
						<font face="GothamBold" color={Styling.TEXT_BLUE2} size="16">
							CASSETTE 1 : VIAL 1
						</font>
					</label>
					<frame />
					<columns gapH="10" widths="17%,83%">
						<rows gapV="10">
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									NAME
								</font>
							</label>
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									DESCRIPTION
								</font>
							</label>
						</rows>
						<rows gapV="10">
							<label useEmbedded="true" alignH="left" alignV="centre">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="16">
									HBr
								</font>
							</label>
							<label useEmbedded="true" alignH="left" alignV="centre">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="16">
									Hydrobromic acid in acetic acid
								</font>
							</label>
						</rows>
					</columns>
					<frame />
				</rows>
			</columns>;

		// Edit cassette XML
		protected static const EDIT_CASSETTE:XML = 
			<columns gapH="0" widths="6%,88%,6%">
				<frame />
				<rows background={Styling.APPLICATION_BACKGROUND} gapV="0" heights="2%,8%,10,18%,72%">
					<frame />
					<label useEmbedded="true" alignH="left" alignV="centre">
						<font face="GothamBold" color={Styling.TEXT_BLUE2} size="16">
							CASSETTE 1 : VIAL 1
						</font>
					</label>
					<frame />
					<columns gapH="10" widths="17%,83%">
						<rows gapV="10">
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									NAME
								</font>
							</label>
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									DESCRIPTION
								</font>
							</label>
						</rows>
						<rows gapV="10" heights="50%,50%">
							<frame alignH="fill">
								<input id="reagentname" alignH="fill" color={Styling.TEXT_GRAY1} 
										size="22" skin={getQualifiedClassName(TextInput_upSkin)} 
										returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
							</frame>
							<frame alignH="fill">
								<input id="reagentdescription" alignH="fill" color={Styling.TEXT_GRAY1} 
										size="22" skin={getQualifiedClassName(TextInput_upSkin)} 
										returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
							</frame>
						</rows>
					</columns>
					<frame />
				</rows>
			</columns>;

		// Run cassette XML
		protected static const RUN_CASSETTE:XML = 
			<frame />;
	}
}
